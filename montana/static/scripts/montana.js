$(document).ready(function() {
    $.getJSON('api/events', function showEvents(data) {
        body = $('body');
        $.each(data.services, function(i, service) {
            body.append($('<p>Recent "' + service.service + '" events at ' + service.host + ':</p>'));
            var list = $('<ul>').appendTo(body);
            $.each(service.events, function(i, event) {
                list.append($('<li>').text(event.logged + ': ' + event.service + ' @ ' + event.host + ' (' + event.status + ')'));
            });
        });
    });
});
