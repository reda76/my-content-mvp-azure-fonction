import azure.functions as func
import logging
import pandas as pd
import scipy.sparse as sparse
import pickle
import json

app = func.FunctionApp()

def recommandation_5(USER_ID):
    print("Entré en fonction")
    # import du modele
    colab_model = pickle.load(open("colab_model.sav", 'rb'))
    
    # import de la dataframe
    collab_data_df = pd.read_csv("collab_data_df.csv")
    
    sparse_user_item = sparse.csr_matrix(
    (collab_data_df['interactionStrength'].astype(float),
     (collab_data_df['user_id'], collab_data_df['article_id_encode'])))
    item_ids, scores = colab_model.recommend(USER_ID,
                                             sparse_user_item[USER_ID],
                                             N=5,
                                             filter_already_liked_items=True)
    article_recommandes = {}
    for i in zip(item_ids, scores):
        article_recommandes[str(i[0])] = str(i[1])

    article_recommandes = json.dumps(article_recommandes)
    
    return article_recommandes

@app.function_name(name="HttpTrigger1")
@app.route(route="recommandation", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
     logging.info('Python HTTP trigger function processed a request.')

     user_id = req.params.get('user_id')
     recommandation_id = recommandation_5(int(user_id))
     print("recommndation id variable")
     print(recommandation_id)
     if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('user_id')

     if user_id: 
        return func.HttpResponse(recommandation_id)
     else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )