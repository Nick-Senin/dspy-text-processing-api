import dspy
import config
from metrics.assess_banal import banal_metric
from metrics.assess_reproducibility import reproducibility_metric
from modules.enrich import TripletEnricher


def process_text(extractor, text, banal_threshold=config.BANAL_THRESHOLD, reproducibility_threshold=0.7):
    """
    Выполняет полный цикл: извлечение, фильтрация по банальности, обогащение и оценка воспроизводимости.
    Возвращает отфильтрованные и неотфильтрованные связки, а также строку с информацией об отфильтрованных.
    """
    prediction = extractor(initial_text=text)

    if not prediction.transformations:
        return [], [], "Не удалось извлечь преобразования."

    unfiltered_triplets = prediction.transformations
    non_banal_triplets = []
    failed_triplets_details = []

    for t in unfiltered_triplets:
        single_prediction = dspy.Prediction(transformations=[t])
        banal_score, failed_triplets_info = banal_metric(single_prediction, return_details=True)

        if banal_score > banal_threshold:
            non_banal_triplets.append(t)
        else:
            for failed in failed_triplets_info:
                details = f"""Отфильтрована по банальности:
Начальное состояние: {failed['initial_state']}
Преобразование: {failed['transformation']}
Результат: {failed['result']}
Банальность: {failed['banality_score']:.2f}"""
                details += f"\n Связки, сгенерированные LLM : {str(failed['generated_banal_transformations'])}"
                details += f"\n --------------"
                failed_triplets_details.append(details)

    if not non_banal_triplets:
        return [], unfiltered_triplets, "\n".join(failed_triplets_details)

    enricher = TripletEnricher()
    enriched_triplets = [enricher(initial_text=text, transformation_triplet=t) for t in non_banal_triplets]
    
    final_triplets = []
    for triplet in enriched_triplets:
        single_prediction = dspy.Prediction(transformations=[triplet])
        repro_score = reproducibility_metric(single_prediction)
        if repro_score >= reproducibility_threshold:
            final_triplets.append(triplet)
        else:
            details = f"Отфильтрована по воспроизводимости: {triplet.get('initial_state', 'N/A')} -> {triplet.get('transformation', 'N/A')} -> {triplet.get('result', 'N/A')} (Воспроизводимость: {repro_score:.2f})"
            failed_triplets_details.append(details)
            
    return final_triplets, unfiltered_triplets, "\n".join(failed_triplets_details)