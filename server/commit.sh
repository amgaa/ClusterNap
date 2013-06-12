#! /bin/sh

git pull
git add .
git commit -m "from commiter. Edited files"
git push

git add -u
git commit -m "from commiter. Deleted files"
git push
