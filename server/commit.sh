#! /bin/sh

git pull
git add .
git commit -m "from commiter"
git push

git add -u
git commit -m "from commiter"
git push
