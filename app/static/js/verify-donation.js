function verify_donation(changeElem, linkElem, donationId) {
  $.post('/verify_donation', {
    id: donationId
  }).done(function(response) {
    if (response['success']) {
      $(changeElem).text('verified');
      $(changeElem).removeClass('badge-danger').addClass('badge-success');
      $(linkElem).remove();
    } else {
      alert("Invalid donation");
    }
  }).fail(function() {
    alert("Server error");
  });
}
