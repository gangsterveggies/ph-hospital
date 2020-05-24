function confirm_pledge(elemId, pledgeId) {
  var $mainElem = $("#item-pledge-" + elemId.toString());
  $.post('/confirm_pledge', {
    id: pledgeId
  }).done(function(response) {
    if (response['success']) {
      $mainElem.children().remove();
      $mainElem.append("<span class=\"badge badge-success\">Pledge Confirmed!</span>");
    } else {
      alert("Something went wrong, please refresh the page and try again.");
    }
  }).fail(function() {
    alert("Something went wrong, please refresh the page and try again.");
  });
}
