/**
 * Adjust the indices of form fields when removing items.
 */
function adjustIndices(removedIndex) {
  var $forms = $('.supply-entry');

  $forms.each(function(i) {
    var $form = $(this);
    var index = parseInt($form.data('index'));
    var newIndex = index - 1;

    if (index < removedIndex) {
      // Skip
      return true;
    }

    $form.find('label').each(function(idx) {
      var $item = $(this);
      $item.attr('for', $item.attr('for').replace(index, newIndex));
    });

    $form.find('select').each(function(idx) {
      var $item = $(this);
      $item.attr('id', $item.attr('id').replace(index, newIndex));
      $item.attr('name', $item.attr('name').replace(index, newIndex));
    });

    $form.find('input').each(function(idx) {
      var $item = $(this);
      $item.attr('id', $item.attr('id').replace(index, newIndex));
      $item.attr('name', $item.attr('name').replace(index, newIndex));
      $item.val('');
    });

    $form.data('index', newIndex);

    return true;
  });
}

/**
 * Remove a subform.
 */
function removeForm() {
  console.log("here");
  var $removedForm = $(this).closest('.supply-entry');
  var removedIndex = parseInt($removedForm.data('index'));

  $removedForm.remove();

  // Update indices
  adjustIndices(removedIndex);
}

/**
 * Add a new subform.
 */
function addForm() {
  // Get Last index
  var $lastForm = $('.supply-entry').last();
  var $templateForm = $('.supply-entry').first();

  var newIndex = 0;

  if ($lastForm.length > 0) {
    newIndex = parseInt($lastForm.data('index')) + 1;
  }

  // Maximum of 10 subforms
  if (newIndex > 9) {
    console.log('[WARNING] Reached maximum number of elements');
    return;
  }

  // Add elements
  var $newForm = $templateForm.clone();

  $newForm.find('label').each(function(idx) {
    var $item = $(this);
    $item.attr('for', $item.attr('for').replace('0', newIndex));
  });

  $newForm.find('select').each(function(idx) {
    var $item = $(this);
    $item.attr('id', $item.attr('id').replace('0', newIndex));
    $item.attr('name', $item.attr('name').replace('0', newIndex));
  });

  $newForm.find('input').each(function(idx) {
    var $item = $(this);
    $item.attr('id', $item.attr('id').replace('0', newIndex));
    $item.attr('name', $item.attr('name').replace('0', newIndex));
    $item.val('');
  });

  $newForm.data('index', newIndex);
  $newForm.append("<div class=\"col-md-1 pt-4 mb-3\"><button type=\"button\" class=\"close remove-entry\" ><i class=\"fa fa-trash\" aria-hidden=\"true\"></i></button></div>");

  // Append
  $('#supply-entries').append($newForm);
  $newForm.find('.remove-entry').click(removeForm);
}


$(document).ready(function() {
  $('#add-entry').click(addForm);
  $('.remove-entry').click(removeForm);
});
