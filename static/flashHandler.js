const flashMessage = document.getElementsByClassName('alert')[0]

if (document.getElementsByClassName('alert')[0]){
    window.setTimeout("flashMessage.style.display='none';", 2000);
}
