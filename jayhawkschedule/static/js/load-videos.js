$(document).ready(function() {
    $('.video').each(function() {
        var video_id = $('div',this).attr("id");
        $(this).append('<script src="http://player.espn.com/player.js?playerBrandingId=4ef8000cbaf34c1687a7d9a26fe0e89e&adSetCode=91cDU6NuXTGKz3OdjOxFdAgJVtQcKJnI&pcode=1kNG061cgaoolOncv54OAO1ceO-I&externalId=espn:'+video_id+'&thruParam_espn-ui[autoPlay]=false&thruParam_espn-ui[playRelatedExternally]=true&targetReplaceId='+video_id+'"></script>');
    }); 
});