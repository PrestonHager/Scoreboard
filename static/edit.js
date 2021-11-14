function editListing(id) {
  $("div#listing-data-" + id).hide();
  $("div#listing-entry-" + id).css('display', 'flex');
}

function editListingDone(id) {
  $("div#listing-entry-" + id).hide();
  let data = {
    listing_id: id
  };
  let name = $("input#entry-name-" + id).val();
  let total = $("input#entry-score-" + id).val();
  let oldName = $("span#listing-name-" + id).text();
  let oldTotal = $("span#listing-score-" + id).text();
  if (name !== oldName) {
    data.name = name;
    $("span#listing-name-" + id).text(name);
  }
  if (total !== oldTotal) {
    data.total = total;
    $("span#listing-score-" + id).text(total);
  }
  $.ajax({
    type: "POST",
    url: "edit-listing",
    data: JSON.stringify(data),
    success: function(data) {
      console.log("Successfully edited listing.");
    }
  });
  $("div#listing-data-" + id).css('display', 'flex');
}

function newListing(id) {
  $("ul#listings").append(
    $(`<li id="listing-${id}" class="listing" />`).append(
      $(`<div class="listing-data" id="listing-data-${id}" />`).append(
        $(`<span class="listing-name" />`).append(
          $(`<span id="listing-name-${id}">Unnamed</span>`)
        )
      ).append(
        $(`<span class="listing-score">Score -</span>`).append(
          $(`<span id="listing-score-${id}">0</span>`)
        )
      ).append(
        $(`<span class="listing-actions" />`).append(
          $(`<button class="edit-button" id="action-edit-${id}" onclick="editListing('${id}')" />`).append(
            $(`<i class="fas fa-edit" />`)
          )
        )
      )
    ).append(
      $(`<div class="listing-entry" id="listing-entry-${id}" />`).append(
        $(`<span class="listing-name" />`).append(
          $(`<input id="entry-name-${id}" class="entry-listing-name" value="Unnamed">`)
        )
      ).append(
        $(`<span class="listing-score" />`).append(
          $(`<p>Score -</p>`)
        ).append(
          $(`<span class="input-entry">`).append(
            $(`<input id="entry-score-${id}" class="entry-listing-score" value="0" type="number">`)
          )
        )
      ).append(
        $(`<span class="listing-actions">`).append(
          $(`<button class="delete-button" id="action-delete-${id}" onclick="deleteListing('${id}')" />`).append(
            $(`<i class="fas fa-trash" />`)
          )
        ).append(
          $(`<button class="done-button" id="action-done-${id}" onclick="editListingDone('${id}')">Done</button>`)
        )
      )
    )
  );
}

function deleteListing(id) {
  $("div#popup-delete").show();
  $("button#action-confirm").click((e) => {
    $("div#popup-delete").hide();
    let data = {
      listing_id: id
    };
    $.ajax({
      type: "POST",
      url: "delete-listing",
      data: JSON.stringify(data),
      success: function(data) {
        console.log("Successfully deleted listing.");
        $("li#listing-" + id).remove();
      }
    });
  });
}

$("button#action-add").click((e) => {
  $.ajax({
    type: "POST",
    url: "add-listing",
    data: "{}",
    success: function(data) {
      console.log("Successfully added new listing.");
      let id = data.listing_id;
      newListing(id);
      editListing(id);
    }
  });
});

$("button#action-rename").click((e) => {
  $("#scoreboard-name-entry").show();
  $("#scoreboard-name").hide();
});

$("button#action-rename-done").click((e) => {
  $("div#popup-delete").hide();
  let name = $("input#entry-scoreboard-name").val();
  let oldName = $("span#scoreboard-name").text();
  let data = {};
  if (name !== oldName) {
    data.title = name;
  }
  if (data !== {}) {
    $.ajax({
      type: "POST",
      url: "edit-scoreboard",
      data: JSON.stringify(data),
      success: function(data) {
        console.log("Successfully edited scoreboard.");
        $("span#scoreboard-name").text(name)
        $("#scoreboard-name-entry").hide();
        $("#scoreboard-name").show();
      }
    });
  } else {
    $("#scoreboard-name-entry").hide();
    $("#scoreboard-name").show();
  }
});

$("button#action-cancel").click((e) => {
  $("div#popup-delete").hide();
});
