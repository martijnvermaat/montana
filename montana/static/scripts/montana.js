$(document).ready(function() {
    $.getJSON('api/events', function showEvents(data) {
        body = $('body');
        body.append($('<p>Recent events:</p>'));
        var list = $('<ul>').appendTo(body);
        $.each(data.events, function(i, event) {
            list.append($('<li>').text(event.logged + ': ' + event.service + ' @ ' + event.host + ' (' + event.status + ')'));
        });
    });
});
