from fastapi import FastAPI

from datetime               import datetime, timedelta
from typing                 import Annotated, Union, List

import json
import numpy



from jose                   import JWTError, jwt    # pip install python-jose
from passlib.context        import CryptContext
from pydantic               import BaseModel
from fastapi                import (Depends,
                                    FastAPI,
                                    HTTPException,
                                    status)
from fastapi.security       import (OAuth2PasswordBearer,
                                    OAuth2PasswordRequestForm)

from fastapi.testclient     import TestClient

app = FastAPI()

"""API ON SERVER TO USE DATABASE AND USER CONNEXION"""



DESCRIPTION = "🚀 Obtain semantic segmentation maps of the image " \
            + "in input via DeepLabV3 implemented in PyTorch. "     \
            + "Visit this URL at port 8501 for the streamlit interface."

PATH_DB_USERS    : str = "datas/etablissement_people.json"
PATH_EVALUATIONS : str = "datas/etablissement_evaluations.json"



app = FastAPI(
    title            = "DeepLabV3 image segmentation",
    description      = DESCRIPTION,
    version          = "0.1.0",
    terms_of_service = "",
    openapi_url      = "/website",
    contact          = {"name" : "LAMARQUE Clément",
                        "email": "lamarque.cle@gmail.com"})

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    # RQ : can be generate by :
    #      cryptography.hazmat.primitives import serialization
    #      private_key = open('.ssh/id_rsa', 'r').read()
    #      key = serialization.load_ssh_private_key(private_key.encode(),
    #                                               password=b'')
    # RQ : Cette variable devra futurement être partiellement
    #      ou totalement être transmise par le client
    #      (actuellement 100% serveur)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.get("/")
async def hello():
    return "API IS FUNCTIONAL"

##################
##  API access  ##
##################

class Token    (BaseModel):
    """ access for API """
    access_token : str
    token_type   : str

class TokenData(BaseModel):
    """ username for API connexion """
    username  : Union[str , None] = None

class User     (BaseModel):
    """ key to identify a user in DB """
    uuid      : str
    username  : str

class UserInDB (User):
    """ Password_hash """
    password_hash : str

pwd_context = CryptContext (schemes   = ["bcrypt"],
                            deprecated = "auto")
def verify_password (plain_password,
                     password_hash ) -> bool :
    return pwd_context.verify (plain_password,
                               password_hash)

def get_password_hash (password) -> str :
    return pwd_context.hash(password)

def get_user(db, username: str) -> UserInDB :
    for user in db :
        if username!=user["username"] : continue
        return UserInDB(**user)
    return None

def authenticate_user (fake_db,
                       username: str,
                       password: str) -> dict :
    user = get_user(fake_db, username)
    if user is None:
        return None
    if not verify_password(password,
                           user.password_hash):
        return None
    return user

def create_access_token( data          : dict,
                         expires_delta : Union[timedelta, None] = None
                       ) -> str :
    to_encode = data.copy()
    moretime  = expires_delta if expires_delta else timedelta(minutes=15)
    expire    = datetime.utcnow() + moretime
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
        db_users = json.load(fichier)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc

    user = get_user(db_users, username=token_data.username)
    if user is None : raise credentials_exception
    return user
    # NB : if we want add a param of user activity "disabled"
    #async def get_current_active_user(current_user: Annotated[User,
    #                                  Depends(get_current_user)]):
    #    if current_user.disabled:
    #         raise HTTPException(status_code=400, detail="Inactive user")
    #    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,
                                                      Depends()]
                                ) -> dict :

    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
        db_users = json.load(fichier)

    user = authenticate_user(db_users, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Incorrect username or password",
            headers     = {"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
                    data          = {"sub": user.username},
                    expires_delta = access_token_expires)
    return {"access_token" : access_token,
            "token_type"   : "bearer"}
        # NB : https://jwt.io/ if you want decode "access_token"

'''
################
## USER DATAS ##
################

@app.get("/users/me/items") # , response_model=User)
async def read_own_items( current_user: Annotated[User,
                                                  Depends(get_current_user)]) :

    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
        db_users = json.load(fichier)

    for user in db_users:
        if user["uuid"]!=current_user.uuid : continue
        return user

@app.get("/user/{uuid}/childs")
async def db_have_permit_childs(uuid,
                                current_user: Annotated[User,
                                              Depends(get_current_user)]):
    #if current_user.disabled :
    #    raise HTTPException(status_code=400, detail="Inactive user")

    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
        db_users = json.load(fichier)

    user = [db_user for db_user in db_users if db_user["uuid"]== uuid]
    detail = "Dans la BDD, aucun utilisateur est associé à l'uuid entré."
    if len(user)==0: raise HTTPException(status_code=400, detail=detail)
    detail = "Dans la BDD, plus d'un utilisateur est associé à l'uuid entré."
    if len(user)>=2: raise HTTPException(status_code=400, detail=detail)
    user=user[0]

    user_uuid = user["uuid"       ]
    user_role = user["actual_role"][0]
        # RQ : strusture de sortie à étudier dans le cadre
        # ou la personne connectée a plusieurs rôles
        # => on admet pour le moment que seul le premier rôle est retenu

    if   user_role == "child"   :
        for user in db_users:
            if user["uuid"]!=uuid : continue
            return [user]
    elif user_role == "parent"  :
        db_childs = [i for i in db_users  if "child"   in i["actual_role"]]
        db_childs = [i for i in db_childs if user_uuid in i["familly"    ]]
        return db_childs
    elif user_role == "teacher" : # "teacher"
        db_childs = [i for i in db_users if "child" in i["actual_role"]]
        return db_childs
        # NB : on admet pour le moment que teacher a accès à
        # tous les élèves et leurs données
        # dans le cas contraire peut être retourné uniquement l'uuid des élèves
        # triés suivant l'enseignant
    else:
        detail = "L'uuid entré n'a pas un rôle attendu."
        raise HTTPException(status_code=400, detail=detail)

#@app.get("/users/me/items/uuid")
#async def read_users_me(current_user: Annotated[User,
#                                                Depends(get_current_user)]):
#    return current_user.uuid

#@app.get("/users/all/items")
#async def read_users_me(current_user: Annotated[User,
#                                      Depends(get_current_user)]):
#
#    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
#        db_users = json.load(fichier)
#    return db_users
###########################
##  Evaluations actions  ##
###########################


class Evaluation(BaseModel):
    """ Evaluation class """
    titre     : str
    uuid      : str
    category  : str
    beginning : Union[str , None]
    collecte  : Union[str , None]
    rendu     : Union[str , None]
    knowledge_model    : List[str]
    knowledge_NotModel : List[str]
    childs_evaluated   : List[str]
    #"eleves_non_evaluated" : ["uuid5"],
    #"classe_concernée"  : ["class_uuid"]

# Intégrer dans la DB une évaluation créée
#@app.post("/add_evaluation/")
#async def send_evaluation(evaluation: Evaluation,
#                          current_user: Annotated[User,
#                                        Depends(get_current_user)]):
#
#    with open(PATH_EVALUATIONS , 'r', encoding="utf-8") as fichier:
#        db_evals = json.load(fichier)#
#
#    db_evals += [evaluation.__dict__]
#
#    with open(PATH_EVALUATIONS , 'w', encoding='utf-8') as file:
#        json.dump(db_evals, file, ensure_ascii = False, indent = 4)
#    return None

# Mettre à jour les caractéristiques d'une évaluation
@app.post("/add_evaluation/")
async def add_evaluation (evaluation   : Evaluation,
                          current_user : Annotated[User,
                                                   Depends(get_current_user)]
                         ) -> None :

    with open(PATH_EVALUATIONS , 'r', encoding="utf-8") as fichier:
        db_evals = json.load(fichier)

    evaluation = evaluation.__dict__
    if evaluation in db_evals :
        db_evals = list(map(
            lambda x : x if x["uuid"] != evaluation["uuid"] else evaluation,
            db_evals))
    else :
        db_evals += [evaluation]

    #in_db_evals = False
    #new_db_evals = []
    #for db_eval in db_evals :
    #    if db_eval["uuid"] != evaluation["uuid"] :
    #        new_db_evals += [db_eval]
    #    else :
    #        in_db_evals = True
    #        new_db_evals += [evaluation]
    #if not in_db_evals :
    #    new_db_evals += [evaluation]
    # db_evals = new_db_evals

    with open(PATH_EVALUATIONS , 'w', encoding='utf-8') as file:
        json.dump(db_evals, file, ensure_ascii = False, indent = 4)
    return None

# Supprimer une évaluation
@app.post("/delete_evaluation/")
async def delete_evaluation( evaluation   : Evaluation,
                             current_user : Annotated[User,
                                                      Depends(get_current_user)]
                            ) -> None :

    with open(PATH_EVALUATIONS , 'r', encoding="utf-8") as fichier:
        db_evals = json.load(fichier)

    evaluation = evaluation.__dict__
    if evaluation in db_evals:
        db_evals.remove(evaluation)
        with open(PATH_EVALUATIONS , 'w', encoding='utf-8') as file:
            json.dump(db_evals, file, ensure_ascii = False, indent = 4)
        return None

    #new_db_evals = []
    #in_db_evals = False
    #for db_eval in db_evals :
    #    if db_eval["uuid"] != evaluation["uuid"] :
    #        new_db_evals += [db_eval]
    #    else :
    #        in_db_evals = True

    #if in_db_evals :
    #    with open(PATH_EVALUATIONS , 'w', encoding='utf-8') as file:
    #        json.dump(new_db_evals, file, ensure_ascii = False, indent = 4)
    #    return None

    detail = "Cette évaluation n'a pas pû être retrouvée et supprimée de la BDD"
    raise HTTPException(
            status_code="200",
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"})



class Evaluation_results (BaseModel):
    """ Description of the results for an evaluation """
    uuid                                : str
    childs_uuid                         : List[str]
    childs_competences                  : List[List[int]]
    etablissement_connaissances_connues : List[str]

# Intégrer les compétences des élèves dans la DB
@app.post("/habilities_evaluation/")
async def habilities_evaluation (evaluation_results : Evaluation_results,
                                 current_user       : Annotated[User,
                                                      Depends(get_current_user)]
                                ) -> None :

    with open(PATH_EVALUATIONS, 'r', encoding="utf-8") as fichier:
        db_evals = json.load(fichier)

    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
        db_peoples = json.load(fichier)

    evaluation_results = evaluation_results.__dict__

    db_evaluations = list(filter(
            lambda db_eval : db_eval["uuid"] == evaluation_results["uuid"],
            db_evals))
    db_evaluation = db_evaluations[0]

    etablissement_connaissances_connues = evaluation_results["etablissement_connaissances_connues"]
    db_evaluation_knowlegdes_model_index = list(map(
        etablissement_connaissances_connues.index,
        db_evaluation["knowledge_model"]))

        # RQ : Certaines compétences peuvent figurer dans "knowledge_notModel",
        #      "etablissement_connaissances_connues.index(i)"
        #      peut dans ce cas retourner None

    db_peoples_uuid = [db_people["uuid"] for db_people in db_peoples]
    evaluation_childs_uuid = evaluation_results["childs_uuid"]

    db_childs_index = []
    for evaluation_child_uuid in evaluation_childs_uuid:
        for i_db_uuid_index, db_people_uuid in enumerate(db_peoples_uuid):
            if evaluation_child_uuid != db_people_uuid : continue
            db_childs_index += [i_db_uuid_index]


    # modification du résumé de compétences des élèves
    childs_competences = evaluation_results["childs_competences"]
    for child_index, db_child_index in enumerate(db_childs_index) :
        for competence_index, db_evaluation_knowlegde_model_index in enumerate(db_evaluation_knowlegdes_model_index):
            db_peoples[db_child_index]["knowledge_Model"][0][db_evaluation_knowlegde_model_index] = \
                    childs_competences[competence_index][child_index]


    # Modification des résultats de l'élève du contrôle dans "results": []
    competences_childs = numpy.transpose(childs_competences, (1,0)).tolist()
    for competences_child, db_child_index in zip(competences_childs,
                                                 db_childs_index):
        evaluation = { "uuid"             : evaluation_results["uuid"],
                       "results_model"    : competences_child,
                       "results_notModel" : [] }
        results = db_peoples[db_child_index]["results"]
        db_people_evals_uuid = [result["uuid"] for result in results]
        is_eval_in_db_evals = None
        for db_eval_index, db_people_eval_uuid in enumerate(db_people_evals_uuid) :
            if db_people_eval_uuid != evaluation_results["uuid"]: continue
            is_eval_in_db_evals = db_eval_index
            break

        if is_eval_in_db_evals is None :
            db_peoples[db_child_index]["results"] += [evaluation]
        else :
            db_peoples[db_child_index]["results"][is_eval_in_db_evals] = evaluation

    try :
        with open(PATH_DB_USERS , 'w', encoding='utf-8') as file:
            json.dump(db_peoples, file, ensure_ascii = False, indent = 4)
            return None
    except Exception as exc :
        detail = "Cette évaluation n'a pas pû être" \
               + f"incorporée ou modifiée dans la BDD : {exc}"
        raise HTTPException( status_code='404',
                             detail=detail,
                             headers={'WWW-Authenticate': 'Bearer'}) from exc

# obtenir toutes les évaluations auxquelles l'utilisateur a accès
@app.get("/user/{uuid}/evals")
async def db_have_permit_evals( uuid,
                                current_user: Annotated[User,
                                              Depends(get_current_user)]):

    with open(PATH_DB_USERS , 'r', encoding="utf-8") as fichier:
        db_users = json.load(fichier)

    user = [db_user for db_user in db_users if db_user["uuid"]== uuid]
    if   len(user)==0 :
        detail = "Dans la BDD, aucun utilisateur est associé à l'uuid entré."
        raise HTTPException( status_code=400, detail=detail)
    if len(user)>=2 :
        detail = "Plus d'un utilisateur est associé à l'uuid entré dans la BDD."
        raise HTTPException( status_code=400, detail=detail)
    user=user[0]

    with open(PATH_EVALUATIONS , 'r', encoding="utf-8") as fichier:
        db_evals = json.load(fichier)

    user_uuid = user["uuid"       ]
    user_role = user["actual_role"][0]
        # RQ : structure de sortie à étudier dans le cadre
        # ou la personne connectée a plusieurs rôles
        # => on admet pour le moment que seul le premier rôle est retenu

    if user_role == "child" :
        user_evals = [db_eval for db_eval in db_evals
                              if user_uuid in db_eval["childs_evaluated"]]
            # RQ : toutes les données des evals sont transmises,
            # même l'uuid des autres élèves qui ne devrait pas l'être
            # => pour chaque db_eval, garder uniquement l'uuid de l"élève
        return user_evals
    if user_role == "parent" :
        db_childs = [i for i in db_users  if "child"   in i["actual_role"]]
        db_childs = [i for i in db_childs if user_uuid in i["familly"    ]]
        childs_evals = []
        for db_eval in db_evals :
            for db_child in db_childs :
                if db_child["uuid"] not in db_eval["childs_evaluated"] :
                    continue
                childs_evals += [db_eval]
                break
        return childs_evals
            # NB : Toutes les evals associées à aumoins
            #      l'un de ses enfants est retourné
    if user_role == "teacher" : # "teacher"
        teacher_db_evals = db_evals
        return teacher_db_evals
            # RQ : on admet pour le moment que teacher a accès à toutes les
            # évals même si elles ne sont pas liées aux "accessible_childs"
    detail = "L'uuid entré n'a pas un rôle attendu."
    raise HTTPException(status_code  = 400,
                        detail       = detail)

###########################################################################
########################  TESTS DE CONTROLE  ##############################
###########################################################################


#client = TestClient(app)
#def test_no_token():
#    response = client.get("/users/me/items")
#    assert response.status_code == 200, response.text
#    assert response.json() == {"msg": "Create an account first"}
'''
