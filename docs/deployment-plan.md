# Deployment Plan

## What The Customer (Nick) Will Do
* He has an [Nginx](https://www.nginx.com/) server instance for us to use.
* He will help us get it running for them and has all the relevant passwords.


## What we will do
* We will likely meet with Nick for a deployment session and get everything we need and set it up with him so he knows exactly how since he is more technically inclined and may want to deploy additions at some later date himself. 
* We will make a specific set of setup instructions as we deploy to the Nginx servers so it can easly by re-deployed at any time by Nick. See [README.md](../README.md) Local Env Setup for an example the type of setup documentation we will make.

## apt-get Installs:
    sudo apt-get install libgeos-dev

## Python Installs:
    sudo pip install -r requirements.txt

### Python Packages:
[See requirements.txt](../requirements.txt)

