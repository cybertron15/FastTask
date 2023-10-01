let invite_button = document.getElementById('invite-btn')
let invite_table = document.getElementById('invites-table')
let fetch_options = {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: null,
}

function get_invite_requests() {
    function show_invites(invites) {
        let tbody = invite_table.getElementsByTagName("tbody")[0];
        tbody.replaceChildren([])
        // Iterate through the data and add rows
        for (const item of invites['invites']) {
            const row = tbody.insertRow();
            const proj_name = row.insertCell(0);
            const owner_name = row.insertCell(1);
            const actions = row.insertCell(2);

            // display project and owner name for each invite and assign invite actions buttons
            proj_name.innerHTML = item.project;
            owner_name.innerHTML = item.owner;
            actions.innerHTML = `<div class="d-flex gap-2">
                                    <img src="/static/accept.png" alt="" class="small-img" invite-id = "${item.id}" action-type="accept">
                                    <img src="/static/cross.png" alt="" class="small-img" invite-id = "${item.id}" action-type="reject">
                                </div>`
        }
    }

    fetch_options.body = JSON.stringify({})
    fetch('http://127.0.0.1:5001/get_invites', fetch_options)
        .then(response => response.json())
        .then(invites => show_invites(invites))
}

function handle_invite_requests(event){
    if (event.target && event.target.tagName == 'IMG') {
        let action = event.target.getAttribute('action-type')
        let invite_id = event.target.getAttribute('invite-id')
        fetch_options.body = JSON.stringify({ 'id': invite_id, 'action': action })

        fetch('http://127.0.0.1:5001/update_invites?kick_user=false', fetch_options)
            .then(response => response.json())
            .then(data => {
                if (data == 'ok') {
                    event.target.parentElement.parentElement.parentElement.remove()
                }
            })
    }
}

invite_button.onclick = get_invite_requests

// code to accept or reject the invite
invite_table.addEventListener('click',handle_invite_requests)