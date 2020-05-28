function pledge_donation(elemId, donationId) {
  var $inputElem = $("#item-request-input-" + elemId.toString());
  var quantity = parseInt($inputElem.val());
  if (quantity == NaN) {
    alert("Invalid quantity.");
  } else {
    $.post('/pledge_donation', {
      id: donationId,
      quantity: quantity
    }).done(function(response) {
      if (response['success']) {
        var $mainElem = $("#item-request-" + elemId.toString());
        $mainElem.children().remove();
        $mainElem.append("<span class=\"badge badge-success\">Pledged " + quantity.toString() + "!</span> <a href=\"/profile\">Go to the Dashboard</a>");
      } else {
        alert("Something went wrong, please refresh the page and try again.");
      }
    }).fail(function() {
      alert("Something went wrong, please refresh the page and try again.");
    });
  }
}
