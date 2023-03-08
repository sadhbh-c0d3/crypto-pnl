SCENARIOS_DIR=$1

for d in $(ls $SCENARIOS_DIR)
do
    ./update-test-scenario.sh $SCENARIOS_DIR/$d
done