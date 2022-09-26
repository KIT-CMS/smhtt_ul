
ERA=$1
CHANNEL=$2
NTUPLETAG=$3
VERSION=$4
SHARDVERSION=$5

# first create the training files
./create_ml_training_files.sh $CHANNEL $ERA $NTUPLETAG $VERSION

# copy the training config
mkdir -p /work/sbrommer/smhtt_ul/training_files/training_$VERSION
cp -r /work/sbrommer/smhtt_ul/training/KingMaker/sm-htt-analysis/v_${VERSION} /work/sbrommer/smhtt_ul/training_files/training_$VERSION

# then run law to create the training
cd "/work/sbrommer/smhtt_ul/training/KingMaker/"
source /work/sbrommer/smhtt_ul/training/KingMaker/setup.sh ML_train


# then run the training
law run RunAllAnalysisTrainings --analysis-config sm-htt-analysis/$VERSION/sm.yaml --RunTraining-production-tag training_${VERSION}_1 --RunTesting-production-tag testing_${VERSION}_1 --CreateTrainingDataShard-production-tag shard_${SHARDVERSION}_1

# copy the testing output
cp /storage/gridka-nrg/sbrommer/LAW_storage/testing_${VERSION}_1/RunTesting/sm_${ERA}_${CHANNEL}/keras_test_results.tar.gz /work/sbrommer/smhtt_ul/training_files/training_$VERSION

# untar the testing output
cd "/work/sbrommer/smhtt_ul/training_files/training_$VERSION"
tar -xvzf keras_test_results.tar.gz

cd "/work/sbrommer/smhtt_ul/training_files"
# # then run the application
./generate_friends.sh $CHANNEL $ERA $NTUPLETAG training_$VERSION /storage/gridka-nrg/sbrommer/LAW_storage/training_${VERSION}_1/RunTraining/sm_${ERA}_${CHANNEL}/ PRODUCTION
# then run the application
./generate_friends.sh $CHANNEL $ERA $NTUPLETAG training_$VERSION /storage/gridka-nrg/sbrommer/LAW_storage/training_${VERSION}_1/RunTraining/sm_${ERA}_${CHANNEL}/ COLLECT

echo "Done"