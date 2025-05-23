![](![image.png](https://s2.loli.net/2025/05/23/uXZTRo49HeP6vUw.png))

You can reach our project freely through this link [https://docker.ghhu.xin](https://docker.ghhu.xin)

This is a NLP-NER docker based on [huggingface-transformers]( https://github.com/huggingface/transformers) and [Flask](https://flask.palletsprojects.com/en/3.0.x/).
| Load Dataset | Train | Prediction | Evaluate |
| :----------: | :---: | :--------: | :------: |
|      ✔️       |   ✔️   |     ✔️      |    ✔️     |
# Architecture
![](https://s2.loli.net/2024/05/13/2LcRIxyK1dpgvQY.jpg)
# docker usage
see https://hub.docker.com/r/genghonghu/docker-ner for more information.
# How to use?
## Step 1: clone this repository 
``````bash
$ git clone https://github.com/GodHu777777/docker-ner.git
$ cd docker-ner
``````
## Step 2: run NLP-NER image

``````bash
$ docker pull genghonghu/docker-ner:v0.3
$ docker run -it --rm -p 3111:3111 genghonghu/docker-ner:v0.3 # 3111 since flask's port in pod is set to 3111
``````

## Step 4: start the server and get using it

``````bash
$ python3 server.py
``````

After running this command above, there will shows several information about working status, and you can access the given link(default is http://127.0.0.1:5000).

![image.png](https://s2.loli.net/2024/05/13/bKGsm2zqgi9JpWS.png)


# ver Mar 4:

It can be trained by conll2003 and do prediction locally. I am not sure if it is stable in docker container.

# ver Mar 5:

Added simple Flask to present NER result through webpage.

# ver Mar 10:

Added usage document.

TODO: hyper parameters list

`config` file  

# ver Mar 13:

All model(LLM) thing has been transferred into docker container, ` server.py` only do message-transferring work and training(TODO).
