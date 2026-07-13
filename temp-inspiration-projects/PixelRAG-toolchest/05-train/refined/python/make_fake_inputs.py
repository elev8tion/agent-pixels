def make_fake_inputs(processor, batch_size, device):
    from PIL import Image
    import numpy as np

    queries = [f"What is topic number {i}?" for i in range(batch_size)]
    images = []
    for i in range(batch_size):
        arr = np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        images.append(Image.fromarray(arr))

    from train_contrastors import process_queries, process_doc_images

    query_inputs = process_queries(processor, queries)
    doc_inputs = process_doc_images(processor, images)

    query_inputs = {k: v.to(device) for k, v in query_inputs.items()}
    doc_inputs = {k: v.to(device) for k, v in doc_inputs.items()}
    return query_inputs, doc_inputs
