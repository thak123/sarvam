
# How to run?

```bash
#Clean the model directory when you are changing the the embedding size! 
rm -rf tmp/model/* 

python word_vec_run.py --num_epochs=120 --batch_size=128 --vocab_size=80000 --embed_size=128 --window_size=4

python viz_word_vec.py

python command_line_tester.py

#tensorboard
tensorboard --logdir=tmp/model/
#click projector tab and load the vocab file from 
```

# Papers:
- [Glove](https://nlp.stanford.edu/pubs/glove.pdf)
- [NCE Loss](https://arxiv.org/pdf/1410.8251.pdf)
- [Noise Contrasive Estimation](https://papers.nips.cc/paper/5165-learning-word-embeddings-efficiently-with-noise-contrastive-estimation.pdf)
- [Neural Probabilistic Language Models](https://www.cs.toronto.edu/~amnih/papers/ncelm.pdf)
- [Graphical Models for Language Modeling](https://www.cs.toronto.edu/~amnih/papers/threenew.pdf)


# References: 
- http://mccormickml.com/2016/04/27/word2vec-resources/
- https://www.tensorflow.org/tutorials/word2vec
- https://www.analyticsvidhya.com/blog/2017/06/word-embeddings-count-word2veec/

![](https://deeplearning4j.org/img/word2vec_diagrams.png)

![](http://mccormickml.com/assets/word2vec/training_data.png)


```python
# Convert this notebook
! jupyter nbconvert --to markdown --output-dir . README.ipynb
```

    [NbConvertApp] Converting notebook README.ipynb to markdown
    [NbConvertApp] Writing 1204 bytes to ./README.md



```python

```
