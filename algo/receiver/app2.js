let connectionIdx = 0;
let messageIdx = 0;
let img = document.getElementById("pika");

function addConnection(connection) {
  connection.connectionId = ++connectionIdx;
//   addMessage('New connection #' + connectionIdx);

  connection.addEventListener('message', function(event) {
    messageIdx++;
    // const data = JSON.parse(event.data);
    console.log(event.data)
    // document.getElementById("pika").src = event.data
    // const logString = 'Message ' + messageIdx + ' from connection #' +
    //     connection.connectionId + ': ' + data.message;

    // addMessage(logString, data.lang);
    // maybeSetFruit(data.message);
    // document.body.appendChild(document.createElement(event.data))
    // try {
    //     img.src = 'data:image/png;base64,' + event.data
    // } catch {
    //     img.style = `${event.data}`
    // }
    document.body.innerHTML = event.data;
    
    // connection.send('Received message ' + messageIdx);
  });

  connection.addEventListener('close', function(event) {
    addMessage('Connection #' + connection.connectionId + ' closed, reason = ' +
        event.reason + ', message = ' + event.message);
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