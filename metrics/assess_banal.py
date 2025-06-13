import dspy
import json
from typing import List, Tuple, Union
import config

class GenerateBanalTransformations(dspy.Signature):
    """Generate multiple possible transformations given an initial state and a result."""
    initial_state: str = dspy.InputField(desc="The initial state.")
    result: str = dspy.InputField(desc="The resulting state.")
    n: int = dspy.InputField(desc="The number of distinct transformations to generate.")
    generated_transformations: List[str] = dspy.OutputField(desc="A JSON list of generated transformation strings.")

class CompareTransformations(dspy.Signature):
    """Assess the semantic similarity between two transformation descriptions."""
    transformation_one: str = dspy.InputField(desc="The first transformation description.")
    transformation_two: str = dspy.InputField(desc="The second transformation description.")
    similarity_score: float = dspy.OutputField(desc="A score from 0.0 (not at all similar) to 1.0 (semantically identical). Respond with ONLY the floating point number.")

class CausalRelationship(dspy.Signature):
    """Determine if result is a direct logical consequence of initial_state"""
    initial_state: str = dspy.InputField(desc="The initial state.")
    result: str = dspy.InputField(desc="The resulting state.")
    reasoning: str = dspy.OutputField(desc="Explain your reasoning.")
    is_causal: bool = dspy.OutputField(desc="True if there is a clear causal relationship, False otherwise. Respond with ONLY 'True' or 'False'.")

class BanalAssessor(dspy.Module):
    """
    A module to assess the banality of a transformation.
    It works by generating a set of 'banal' transformations from the initial_state and result,
    and then checking if the provided transformation is similar to any of them.
    """
    def __init__(self, n=3):
        super().__init__()
        self.n = n
        self.generate = dspy.ChainOfThought(GenerateBanalTransformations)
        self.compare = dspy.Predict(CompareTransformations)

    def forward(self, initial_state, transformation, result):
        # Step 1: Generate banal transformations
        generated_result = self.generate(initial_state=initial_state, result=result, n=self.n)
        
        try:
            generated_list = generated_result.generated_transformations
            if isinstance(generated_list, str):
                generated_list = json.loads(generated_list)
        except (AttributeError, json.JSONDecodeError, TypeError):
            #print(f"[DEBUG] Failed to generate or parse transformations. Output: {generated_result}")
            return dspy.Prediction(assessment=0.0, generated_transformations=[], similarity_scores=[])

        # Step 2: Compare the provided transformation with each generated one.
        max_similarity = 0.0
        similarity_scores = []  # Сохраняем все оценки сходства
        
        for gen_trans in generated_list:
            comparison_result = self.compare(transformation_one=transformation, transformation_two=gen_trans)
            
            try:
                similarity = float(comparison_result.similarity_score)
                similarity_scores.append({
                    'generated_transformation': gen_trans,
                    'similarity_score': similarity
                })
                if similarity > max_similarity:
                    max_similarity = similarity
            except (ValueError, TypeError, AttributeError):
                #print(f"[DEBUG] Could not convert similarity score '{getattr(comparison_result, 'similarity_score', 'N/A')}' to float.")
                similarity_scores.append({
                    'generated_transformation': gen_trans,
                    'similarity_score': 0.0
                })
                continue
        
        return dspy.Prediction(
            assessment=max_similarity, 
            generated_transformations=generated_list,
            similarity_scores=similarity_scores
        )

def banal_metric(pred, trace=None, return_details=False) -> Union[float, Tuple[float, List[dict]]]:
    """
    Проверяет, что преобразования не являются банальными, используя языковую модель.
    
    Функция оценивает каждое преобразование на предмет банальности, сравнивая его с 
    автоматически сгенерированными "банальными" преобразованиями. Также проводится
    оценка причинно-следственных связей.
    
    Args:
        pred: Объект Prediction, содержащий список преобразований
        trace: Опциональный параметр трассировки для DSPy (не используется)
        return_details: Если True, возвращает кортеж (оценка, список_провалившихся_троек),
                       если False, возвращает только оценку (для совместимости с DSPy)
    
         Returns:
         Union[float, Tuple[float, List[dict]]]: 
             - Если return_details=False: средняя оценка небанальности (float от 0.0 до 1.0)
             - Если return_details=True: кортеж (средняя_оценка, список_провалившихся_троек)
               где список_провалившихся_троек содержит словари с ключами:
               'initial_state', 'transformation', 'result', 'non_banality_score', 'banality_score',
               'generated_banal_transformations', 'similarity_scores', 'max_similarity_score'
    
    Note:
        Функция совместима с DSPy при использовании с параметром return_details=False (по умолчанию).
        Для получения детальной информации используйте return_details=True или 
        вспомогательную функцию get_banal_metric_with_details().
    """
    try:
        transformations_list = pred.transformations
        if not transformations_list:
            return (0.0, []) if return_details else 0.0
    except (AttributeError, KeyError):
        return (0.0, []) if return_details else 0.0

    # Языковая модель должна быть настроена глобально, а не здесь.
    # Если не настроена, dspy.context(lm=...) будет использовать глобальную.
    # Следующий блок закомментирован, так как это не рекомендуемая практика.
    # banal_lm = dspy.LM(
    #     model=config.BANAL_MODEL,
    #     api_key=config.OPENROUTER_API_KEY,
    #     api_base='https://openrouter.ai/api/v1',
    #     max_tokens=500 # Increased for generation
    # )
    
    # Предполагается, что LM настроена глобально, например в main.py
    # dspy.configure(lm=dspy.LM(model=..., api_key=...))
    
    # Оценка причинно-следственной связи с помощью основной модели (вне контекста banal_lm)
    causal_predictor = dspy.ChainOfThought(CausalRelationship)
    
    with dspy.context(lm=dspy.settings.banal_lm):
        assess_banality = BanalAssessor(n=3)
        total_non_banality = 0.0
        num_items = 0
        failed_triplets = []  # Список троек, не прошедших порог банальности

        for p in transformations_list:
            try:
                # Проверяем, что тройка содержит все необходимые поля
                if not all(k in p for k in ['initial_state', 'transformation', 'result']):
                    continue
                
                num_items += 1
                
                # === ОЦЕНКА ПРИЧИННО-СЛЕДСТВЕННОЙ СВЯЗИ ===
                # Используем основную модель (вне контекста banal_lm) для оценки каузальности
                causal_result = causal_predictor(
                    initial_state=p['initial_state'],
                    result=p['result']
                )

                """
                try:
                    is_causal_bool = (str(causal_result.is_causal).lower() == 'true')
                    if is_causal_bool:
                        print(f"✅ Causal (MAIN_MODEL): {p['transformation']} (Reason: {causal_result.reasoning})")
                    else:
                        print(f"❌ Not Causal (MAIN_MODEL): {p['transformation']} (Reason: {causal_result.reasoning})")
                except (ValueError, TypeError, AttributeError):
                    print(f"[DEBUG] Could not parse causal result: {getattr(causal_result, 'is_causal', 'N/A')}")
                """

                # === ОЦЕНКА БАНАЛЬНОСТИ ===
                # Используем специализированную модель (banal_lm) для оценки банальности
                result = assess_banality(
                    initial_state=p['initial_state'],
                    transformation=p['transformation'],
                    result=p['result']
                )

                assessment_value = result.assessment
                banality_score = float(assessment_value) if not isinstance(assessment_value, str) else float(assessment_value.strip())

                # Преобразуем оценку банальности в оценку небанальности (инвертируем)
                # banality_score: 0.0 = не банально, 1.0 = очень банально
                # non_banality_score: 1.0 = не банально, 0.0 = очень банально
                non_banality_score = 1.0 - banality_score
                total_non_banality += non_banality_score

                # === ОБРАБОТКА РЕЗУЛЬТАТОВ ===
                if non_banality_score > config.BANAL_THRESHOLD:
                    # Тройка прошла проверку на банальность
                    print("-" * 5, "НЕБАНАЛЬНОСТЬ > 0.6", "-" * 5)
                    print("Initial state: ", p['initial_state'])
                    print("Transformation: ", p['transformation'])
                    print("Result: ", p['result'])
                    print(f"######### [НЕБАНАЛЬНОСТЬ > 0.6] Transformation: {p['transformation']} (небанальность: {non_banality_score:.2f})")
                else:
                    # Тройка НЕ прошла проверку на банальность
                    # Если запрошены детали, сохраняем информацию о провалившейся тройке
                    if return_details:
                        # Извлекаем информацию о сгенерированных банальных преобразованиях
                        generated_transformations = getattr(result, 'generated_transformations', [])
                        similarity_scores = getattr(result, 'similarity_scores', [])
                        
                        failed_triplets.append({
                            'initial_state': p['initial_state'],
                            'transformation': p['transformation'],
                            'result': p['result'],
                            'non_banality_score': non_banality_score,
                            'banality_score': banality_score,
                            'generated_banal_transformations': generated_transformations,
                            'similarity_scores': similarity_scores,
                            'max_similarity_score': banality_score  # Это и есть максимальная схожесть
                        })
                        
            except (ValueError, TypeError, AttributeError, Exception) as e:
                print(f"[DEBUG] An exception occurred in the banality assessment loop: {e}. Assigning 0.0 non-banality.")
                total_non_banality += 0.0
    
    # === ВОЗВРАТ РЕЗУЛЬТАТОВ ===
    if num_items == 0:
        return (0.0, []) if return_details else 0.0

    # Вычисляем среднюю оценку небанальности
    average_non_banality = total_non_banality / num_items
    
    if return_details:
        # Возвращаем кортеж: (средняя_оценка, список_провалившихся_троек)
        return average_non_banality, failed_triplets
    else:
        # Возвращаем только оценку (для совместимости с DSPy)
        return average_non_banality

def get_banal_metric_with_details(pred, trace=None) -> Tuple[float, List[dict]]:
    """
    Удобная функция-обертка для получения как оценки, так и детальной информации 
    о тройках, не прошедших проверку на банальность.
    
    Эта функция является отдельной для поддержания совместимости с DSPy.
    
    Args:
        pred: Объект Prediction, содержащий список преобразований
        trace: Опциональный параметр трассировки для DSPy (не используется)
    
    Returns:
        Tuple[float, List[dict]]: Кортеж из:
            - float: средняя оценка небанальности (от 0.0 до 1.0)
            - List[dict]: список словарей с информацией о провалившихся тройках,
              каждый содержит:
                * 'initial_state': начальное состояние
                * 'transformation': описание преобразования
                * 'result': результирующее состояние
                * 'non_banality_score': оценка небанальности (0.0-1.0)
                * 'banality_score': оценка банальности (0.0-1.0)
                * 'generated_banal_transformations': список сгенерированных банальных преобразований
                * 'similarity_scores': список с оценками сходства для каждого сгенерированного преобразования
                * 'max_similarity_score': максимальная оценка сходства (= banality_score)
    
    Example:
        >>> score, failed = get_banal_metric_with_details(prediction)
        >>> print(f"Средняя небанальность: {score:.2f}")
        >>> print(f"Количество провалившихся троек: {len(failed)}")
        >>> for triplet in failed:
        ...     print(f"Тройка с небанальностью {triplet['non_banality_score']:.2f}")
        ...     print(f"Сгенерированные банальные преобразования:")
        ...     for sim_data in triplet['similarity_scores']:
        ...         print(f"  - {sim_data['generated_transformation']} (сходство: {sim_data['similarity_score']:.2f})")
    """
    return banal_metric(pred, trace, return_details=True)