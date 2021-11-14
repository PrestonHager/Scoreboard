$('#login-form').submit((e) => {
  e.preventDefault();
  let form_data = $("#login-form").serialize();
  // let form_data = new FormData(this);
  $.ajax({
    type: "POST",
    url: "auth",
    data: form_data,
    success: function(data) {
      window.location.reload();
    }
  });
});
