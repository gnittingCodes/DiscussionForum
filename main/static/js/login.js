const loginButton = document.getElementById('login-btn');
loginButton.addEventListener('click', () => {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  // Send an AJAX request to the server to check the user's credentials
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/login', true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onreadystatechange = () => {
    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      const response = JSON.parse(xhr.responseText);
      if (response.login) {
        // Show the friends section
        showFriendsSection(response.friends_list);
      } else {
        // Display an error message
        displayErrorMessage(response.err_msg);
      }
    }
  };
  xhr.send(`username=${username}&password=${password}`);
});

function showFriendsSection(friendsList) {
    // Create the HTML for the friends section
    const friendsSection = document.createElement('div');
    friendsSection.id = 'friends-section';
    friendsSection.innerHTML = '<h2>Friends List</h2>';
    const list = document.createElement('ul');
    friendsList.forEach(friend => {
      const listItem = document.createElement('li');
      listItem.textContent = friend.name;
      list.appendChild(listItem);
    });
    friendsSection.appendChild(list);
  
    // Add the friends section to the page
    const contentContainer = document.getElementById('content-container');
    contentContainer.appendChild(friendsSection);
  }
  

fetch('/login', {
    method: 'POST',
    body: new FormData(loginForm)
})
.then(response => response.json())
.then(data => {
if (data.login) {
    // Login successful, display friend list
    const friendList = data.friends_list;
    displayFriendList(friendList);
} else {
    // Login failed, display error message
    const errorMessage = data.err_msg;
    displayErrorMessage(errorMessage);
}
})
.catch(error => console.error(error));