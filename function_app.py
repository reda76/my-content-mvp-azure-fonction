import azure.functions as func
import logging
import pandas as pd
import scipy.sparse as sparse
import pickle
import json

app = func.FunctionApp()

def recommandation_5(USER_ID):
    # import du modele
    colab_model = pickle.load(open("colab_model.sav", 'rb'))
    
    # import de la dataframe
    collab_data_df = pd.read_csv("data/collab_data_df.csv")
    
    sparse_user_item = sparse.csr_matrix(
    (collab_data_df['interactionStrength'].astype(float),
     (collab_data_df['user_id'], collab_data_df['article_id_encode'])))
    item_ids, scores = colab_model.recommend(USER_ID,
                                             sparse_user_item[USER_ID],
                                             N=5,
                                             filter_already_liked_items=True)
    
    # Récupère la vrai id des articles et non les encodés
    item_ids_list = item_ids.tolist()
    item_ids_article_id = []
    for i in item_ids_list:
        try:
            item_ids_article_id.append(collab_data_df.loc[collab_data_df['article_id_encode'] == i,
                               'article_id'].values[0])
        except:
            print(i)

    article_recommandes = {}
    for i in zip(item_ids_article_id, scores):
        article_recommandes[str(i[0])] = str(i[1])
    
    
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