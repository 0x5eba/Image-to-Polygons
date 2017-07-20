setInterval( function()
  {
    var img = document.getElementById('immagine')
    img.src = 'pic.png?rand' + Math.random()
}, 1000
);
