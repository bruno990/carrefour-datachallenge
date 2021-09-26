# Desafio do Bootcamp Data Engineer do Banco Carrefour e Digital Innovation One

O desafio:

Desenvolver uma aplicação para monitorar o top trending e seu devido volume na rede social com o passar do tempo:

Funcionalidade #1: Utilizar a api do twitter para consumir o top trending e seu devido volume
Funcionalidade #2: Armazenar o histórico das trendings em um banco de dados noSQL
Funcionalidade #3: Utilizar alguma biblioteca gráfica para exibir os dados
Funcionalidade #4 (opcional): Utilizar IA para análise de sentimento dos tweets referentes aos top trendings.

Para a entrega da solução foi utilizada as seguintes tecnologias/frameworks:

- Lambda functions, CloudWatch e DynamoDB - Cloud AWS
- Dashboard feito usando o framework Streamlit (https://docs.streamlit.io/en/stable/) em Python
- Análise de sentimentos usando o serviço de NLU do IBM Watson

Descrição dos arquivos:

- apiTwitter.py -> Hospedada como função Lambda para obter os trend topics do Twitter e gravar no DynamoDB
- get-twitter.py -> App usando streamlit, hospedado usando instância EC2 da AWS, para exibição dos resultados

O app está disponível em: http://ec2-18-231-157-139.sa-east-1.compute.amazonaws.com:8501
