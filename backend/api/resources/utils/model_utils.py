import resources.utils.models as models
import rasterio
import torch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def load_model(model_path):

    model = models.UNet11()
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    return model

def run_model(patch,model):
    model.eval()
    #print("Model in eval mode")
    with torch.set_grad_enabled(False):
        response = torch.sigmoid(model(patch))
    return response
