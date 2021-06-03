# NLPDashboardServer

This project works in conjunction with NLPDashboard found [here](https://github.com/BinaryWiz/NLPDashboard). It is the backend and manages the SQL database used to store model statistics (accuracy, loss, running accuracy, running loss) as well as information about each example in a batch.

## POST Requests
* `/create_db` - Takes <b>model_name</b> as a parameter and creates a SQL database with that name in the backend.

## DELETE Requests
* `/delete_db` - Takes <b>model_name</b> as a parameter and delete the SQL database with that name in the backend.

## GET Requests
The GET routes used for the server include:
* `/get_batch_data` - Takes <b> model_name, epoch, </b> and <b> batch</b> as parameters and returns the statistics for all the batches that have been put into the server since that epoch/batch.
   * For example, if a model is current on epoch 1 and batch 100 and a request is made with epoch 1 and batch 50, the model will return all 50 batches that after epoch 1, batch 50.
   * The data per batch includes:
      * Loss
      * Accuracy
      * Running Accuracy
      * Running Loss

* `/get_examples_data` - Takes <b> model_name, epoch, </b> and <b> batch</b> as parameters and returns data about each example in the batch.
   * This includes:
      * The first title
      * The second title
      * The softmax's postive output
      * The softmax's negative output
      * The prediction from the model
      * The label

## PUT Requests
The PUT requests used for the server include:
* `/add_batch_data` - Takes <b>model_name</b> and <b>a list of dictionaries</b>. Each dictionary represents a new batch to be added to the server and should include:
   * Epoch
   * Batch
   * Accuracy
   * Loss
   * Running Accuracy
   * Running Loss  

* `/add_examples_data` - Takes <b>model_name</b> and <b>a list of dictionaries</b>. Each dictionary represents an example and should include:
   * Epoch
   * Batch
   * Title 1
   * Title 2
   * Positive Softmax
   * Negative Softmax
   * Model Prediction
   * Label
