SCENARIOS_DIR=$1

for d in $(ls $SCENARIOS_DIR)
do
    ./run-test-scenario.sh $SCENARIOS_DIR/$d
done