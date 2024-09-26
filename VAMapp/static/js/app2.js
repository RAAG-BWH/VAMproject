let connectionIdx = 0;
let messageIdx = 0;
let img = document.getElementById("pika");

function addConnection(connection) {
  connection.connectionId = ++connectionIdx;
//   addMessage('New connection #' + connectionIdx);

  connection.addEventListener('message', function(event) {
    messageIdx++;
    console.log(event.data)
    document.body.innerHTML = event.data;
  });

  connection.addEventListener('close', function(event) {
    addMessage('Connection #' + connection.connectionId + ' closed, reason = ' +
        event.reason + ', message = ' + event.message);
    connection.send("hola");
  });

  connection.addEventListener('terminate', function(event) {
    connection.send("hola");
  });
};

document.addEventListener('DOMContentLoaded', function() {
    if (navigator.presentation.receiver) {
      navigator.presentation.receiver.connectionList.then(list => {
        list.connections.map(connection => addConnection(connection));
        list.addEventListener('connectionavailable', function(event) {
          addConnection(event.connection);
        });
      });
    }
  });