# Image Synthesis Using Variational Autoencoders with Adversarial Learning

## Reproduction & comparison study
In this project, we analyze the adversarial generator encoder ([AGE](https://arxiv.org/pdf/1807.06358.pdf)) and the introspective autoencoder ([IntroVAE](https://arxiv.org/pdf/1807.06358.pdf)). 

Here is the structure and training flow of 1)VAE, 2)AGE, and 3)IntroVAE:

<img width="561" alt="structure" src="https://user-images.githubusercontent.com/37233460/66704951-2e6b5300-ed21-11e9-9cee-6cadbd7ecae9.png">

And the detailed network architecture for encoding images of 128\*128 resolution in IntroVAE(top) and AGE(bottom).

<img width="543" alt="arch" src="https://user-images.githubusercontent.com/37233460/66704971-670b2c80-ed21-11e9-9937-0edb50aef6b6.png">

We implement the models from scratch and apply them to CIFAR-10 and CelebA image datasets for unconditional image generation and reconstruction tasks. For CIFAR-10, we evaluate AGE quantitatively and our model reaches an Inception score of 2.90. AGE does not converge on the higher resolution dataset CelebA, whereas IntroVAE reaches stable training but suffer from blurriness and sometimes mode collapse.

## Dataset

## Experiments

## Result

Here are some examples of our results:

<img width="535" alt="cifar10" src="https://user-images.githubusercontent.com/37233460/66704979-899d4580-ed21-11e9-8c01-4a9aafe51267.png">

<img width="320" alt="celebA" src="https://user-images.githubusercontent.com/37233460/66704994-b7828a00-ed21-11e9-8669-3c4c8c0eaf9f.png">



### Useful link:


