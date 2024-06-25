from ultralytics import YOLO, COCOEval


model_path = "path/to/your/trained/model.pt"  # Put do modela
data_path = "path/to/your/test/dataset"  # put do baze

# pokreni
model = YOLO(model_path)

#
device = model.device  # pozovi isti model

# git
evaluator = COCOEval(data_path, task="val", img_size=model.hyp["image_size"])  # sliek/

# pokreni model na dataset
model.eval()  # podesi ga na "evaluation mod"
for image, targets in model.dataloader(data_path):
    # pozovi ga
    image, targets = image.to(device), targets.to(device)
    # predikcije
    with torch.no_grad():
        preds = model(image)
    # ovdje trebacocoeval
    evaluator.update(preds, targets)

# printaj metriku
evaluator.summarize()