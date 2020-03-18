#! /bin/bash
set -x 
BUILDPATH="target"
CODEBUILD_SRC_DIR="."
APPNAME="$1"

# install deps
pip install -r requirements.txt -t $CODEBUILD_SRC_DIR/$BUILDPATH
# copy all lingering python files
cp ./*.py $CODEBUILD_SRC_DIR/$BUILDPATH

(cd $BUILDPATH && zip -r ../$APPNAME.zip .)
