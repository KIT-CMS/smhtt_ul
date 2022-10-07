
ERA=$1
CHANNELS=$2
NTUPLETAG=$3
VERSION=$4
SHARDVERSION=$5

# # first create the training files
# ./create_ml_training_files.sh $CHANNELS $ERA $NTUPLETAG $VERSION

# # copy the training config
# mkdir -p /work/sbrommer/smhtt_ul/training_files/training_$VERSION
# cp -r /work/sbrommer/smhtt_ul/training/KingMaker/sm-htt-analysis/${VERSION} /work/sbrommer/smhtt_ul/training_files/training_$VERSION

# # then run law to create the training
# cd "/work/sbrommer/smhtt_ul/training/KingMaker/"
# source /work/sbrommer/smhtt_ul/training/KingMaker/setup.sh ML_train


# # then run the training
# law run RunAllAnalysisTrainings --analysis-config sm-htt-analysis/$VERSION/sm.yaml --RunTraining-production-tag training_${VERSION}_1 --RunTesting-production-tag testing_${VERSION}_1 --CreateTrainingDataShard-production-tag shard_${SHARDVERSION}_1

# copy the testing output
cd "/work/sbrommer/smhtt_ul/training_files/training_$VERSION"
for FOLDER in /storage/gridka-nrg/sbrommer/LAW_storage/testing_${VERSION}_1/RunTesting/sm_${ERA}_* ; do
    cp $FOLDER/keras_test_results.tar.gz /work/sbrommer/smhtt_ul/training_files/training_$VERSION
    # untar the testing output
    tar -xvzf keras_test_results.tar.gz
done
cd "/work/sbrommer/smhtt_ul/training_files"
# # then run the application
./generate_friends.sh $CHANNELS $ERA $NTUPLETAG training_$VERSION /storage/gridka-nrg/sbrommer/LAW_storage/training_${VERSION}_1/RunTraining/ PRODUCTION
# then run the application
./generate_friends.sh $CHANNELS $ERA $NTUPLETAG training_$VERSION /storage/gridka-nrg/sbrommer/LAW_storage/training_${VERSION}_1/RunTraining/ COLLECT

echo "Done"