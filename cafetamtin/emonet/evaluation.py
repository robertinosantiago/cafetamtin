import numpy as np
import torch

def evaluate_metrics(ground_truth, predictions, metrics, verbose=True, print_tex=True):
    results = {}
    for name, metric in metrics.items():
        results[name] = metric(ground_truth, predictions)
    if verbose:
        print(', '.join(f'{name}={results[name]:.2f}' for name in metrics))
    elif print_tex:
        tex = ' & '.join(f'{results[name]:.2f}' for name in metrics)
        print(tex)

    return results

# Test loop
def evaluate(net, dataloader, device, metrics_valence_arousal=None, metrics_expression=None, metrics_au=None, verbose=True, print_tex=False):

    net.eval()

    for index, data in enumerate(dataloader):

        #images = data['image'].to(device)
        images = data['image'].to()
        print("imagem = ", images)
        valence = data.get('valence', None)
        arousal = data.get('arousal', None)
        expression = data.get('expression', None)

        with torch.no_grad():
            out = net(images)
      
        #shape_pred = out['heatmap']
        if expression is not None:
            expr = out['expression']
            expr = np.argmax(np.squeeze(expr.cpu().numpy()), axis=1)

        if metrics_valence_arousal is not None:
            val = out['valence']
            ar = out['arousal']

            val = np.squeeze(val.cpu().numpy())
            ar = np.squeeze(ar.cpu().numpy())

        if index:
            if metrics_valence_arousal is not None:
                valence_pred = np.concatenate([val, valence_pred])
                arousal_pred = np.concatenate([ar,  arousal_pred])
                valence_gts = np.concatenate([valence, valence_gts])
                arousal_gts = np.concatenate([arousal,  arousal_gts])
        
            if expression is not None:        
                expression_pred = np.concatenate([expr, expression_pred])
                expression_gts = np.concatenate([expression, expression_gts])
        else:
            if metrics_valence_arousal is not None:
                valence_pred = val
                arousal_pred = ar
                valence_gts = valence
                arousal_gts = arousal

            if expression is not None:    
                expression_pred = expr
                expression_gts = expression
            

        print("valencia = ", valence_pred, "\narousal = ", arousal_pred, "\nexpression = ", expression_pred, "\n\n")            
