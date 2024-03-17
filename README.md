This is a NLP-NER docker based on [huggingface-transformers]( https://github.com/huggingface/transformers) and [Flask](https://flask.palletsprojects.com/en/3.0.x/).

| Load Dataset | Train | Prediction | Evaluate |
| :----------: | :---: | :--------: | :------: |
|      ❌       |   ✔️   |     ✔️      |    ❌     |

# docker usage

see https://hub.docker.com/r/genghonghu/docker-ner for more information.

# How to use?

## Step 1: clone this repository 

``````bash
$ git clone https://github.com/GodHu777777/docker-ner.git
$ cd docker-ner
``````

## Step 2: run the commands of ```run.sh```

``````bash
$ bash run.sh
``````

## Step 3: wait for training

It may take several minutes or even more than one hour.

## Step 4: start the project

``````bash
$ flask --app app run
``````

After running this command above, there will shows several information about working status, and you can access the given link(default is http://127.0.0.1:5000).

![working status](https://s2.loli.net/2024/03/10/KmrwRaqoQ6e74P8.png)

## Step 5: get using it 

Open a browser and type the link, you can now use it to do any NER task on you own!

![webpage appearance](https://s2.loli.net/2024/03/10/3aiHnKtzZhEGbTS.png)

# ver Mar 4:

It can be trained by conll2003 and do prediction locally. I am not sure if it is stable in docker container.

# ver Mar 5:

Added simple Flask to present NER result through webpage.

# ver Mar 10:

Added usage document.

TODO: hyper parameters list

`config` file  