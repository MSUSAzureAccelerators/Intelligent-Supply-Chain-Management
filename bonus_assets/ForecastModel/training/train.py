from gluonts.dataset.common import load_datasets, ListDataset
from gluonts.dataset.field_names import FieldName
#from gluonts.model.deepar import DeepAREstimator
from gluonts.mx import DeepAREstimator #changed this
from gluonts.mx.distribution.gaussian import GaussianOutput
from gluonts.mx.trainer import Trainer
from gluonts.evaluation.backtest import make_evaluation_predictions
from gluonts.evaluation import make_evaluation_predictions, Evaluator
import pandas as pd 
import os
import pickle
import argparse
import numpy as np
import mlflow

from azureml.core import Workspace, Dataset, Experiment
from azureml.core.run import Run


def load_data(workspace, dataset_name, prediction_length, context_length):
    
    dataset = Dataset.get_by_name(workspace, name=dataset_name, version='latest')
    with dataset.mount() as dataset_context: 
        dataset_context.start()
        sales_data = pd.read_csv(os.path.join(dataset_context.mount_point, f"{dataset_name}.csv"))

    start = sales_data.Date.min()
    end = sales_data.Date.max()
    ensemble = []
    dates = list(pd.date_range(start, end))
    
    item_to_class = {}
    for item, cls in zip(sales_data.Item.values, sales_data["Item Class"].values): 
        if item not in item_to_class: 
            item_to_class[item] = cls

    for item in set(sales_data.Item): 
        for location in set(sales_data.Location):
            sales = sales_data[(sales_data.Item == item) & (sales_data.Location == location)].Sales.values
            if len(sales): 
                scale = max(abs(sales))
                ensemble.append(
                    {
                        "class": item_to_class[item],
                        "item": item,
                        "sales": sales,
                        "start": start,
                        "end": end,
                        "total": sum(sales),
                        "scale": scale,
                        "location": location,
                        "sales_scaled": sales / scale,
                    }
                )
    ensemble = sorted(ensemble, key=lambda k: k["total"], reverse=True)

    quantity_length = len(ensemble[0]["sales"])
    static_cats = [(e["class"].strip(), e["item"].strip(), e["location"].strip()) for e in ensemble]

    item_to_index = {item: idx for idx, item in enumerate(set([sc[0] for sc in static_cats]))}
    item_class_to_index = {item: idx for idx, item in enumerate(set([sc[1] for sc in static_cats]))}
    location_to_index = {loc: idx for idx, loc in enumerate(set([sc[2] for sc in static_cats]))}

    test_target_values = np.array([np.array(e["sales_scaled"]) for e in ensemble])
    train_target_values = np.array([np.array(e["sales_scaled"][:-prediction_length]) for e in ensemble])


    train_ds = ListDataset([
        {
            FieldName.TARGET: target,
            FieldName.START: start,
            FieldName.FEAT_STATIC_CAT: [
                item_to_index[sc_item], 
                item_class_to_index[sc_item_class], 
                location_to_index[sc_location]
            ],
        }
        for target, (sc_item, sc_item_class, sc_location) in zip(train_target_values, static_cats)
    ], freq="D")

    test_ds = ListDataset([
        {
            FieldName.TARGET: target,
            FieldName.START: start,
            FieldName.FEAT_STATIC_CAT: [
                item_to_index[sc_item], 
                item_class_to_index[sc_item_class], 
                location_to_index[sc_location]
            ],
        }
        for target, (sc_item, sc_item_class, sc_location) in zip(test_target_values, static_cats)
    ], freq="D")
    return train_ds, test_ds, item_to_index, item_class_to_index, location_to_index



def main():

    # get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str, default='synthesized-sales')
    
    # hyperdrive related arguments:
    parser.add_argument('--epochs', type=int, default=20, help='number of epochs to train')
    parser.add_argument('--learning_rate', type=float, default=1e-2, help='learning rate')
    parser.add_argument('--num_batches_per_epoch', type=int, default=10)
    parser.add_argument('--prediction_length', type=int, default=30)
    parser.add_argument('--context_length', type=int, default=5*30)
    parser.add_argument('--local', type=bool, default=False)
   
    args = parser.parse_args()

    if not args.local:
        run = Run.get_context()
        workspace = run.experiment.workspace
    else: 
        workspace = Workspace.from_config()

    # load data
    train_ds, test_ds, item_to_index, item_class_to_index, location_to_index = load_data(workspace, args.dataset_name, args.prediction_length, args.context_length)

    # init model
    estimator = DeepAREstimator(
        prediction_length=args.prediction_length,
        context_length=args.context_length,
        freq="D",
        num_cells = 2,
        distr_output = GaussianOutput(),
        use_feat_dynamic_real=False,
        use_feat_static_cat=True,
        cardinality=[len(item_to_index), len(item_class_to_index), len(location_to_index)],
        embedding_dimension=[32,64, 32],
        trainer=Trainer(
            learning_rate=args.learning_rate,
            epochs=args.epochs,
            num_batches_per_epoch=args.num_batches_per_epoch,
            clip_gradient=1.0
        )
    )

    # run training
    predictor = estimator.train(train_ds)

    # save model
    os.makedirs("outputs/model", exist_ok=True)
    with open("outputs/model/predictor.pkl", "wb") as f: 
        pickle.dump(predictor, f)


if __name__ == "__main__":
    try:
        import mlflow
        with mlflow.start_run():
            main()
    except: 
        main()
