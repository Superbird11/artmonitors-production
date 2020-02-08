// ref: http://stackoverflow.com/a/1293163/2343
// This will parse a delimited string into an array of
// arrays. The default delimiter is the comma, but this
// can be overriden in the second argument.
function CSVToArray( strData, strDelimiter ){
    // Check to see if the delimiter is defined. If not,
    // then default to comma.
    strDelimiter = (strDelimiter || ",");
    // Create a regular expression to parse the CSV values.
    var objPattern = new RegExp(
        (
            // Delimiters.
            "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +

            // Quoted fields.
            "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

            // Standard fields.
                "([^\"\\" + strDelimiter + "\\r\\n]*))"
        ), "gi" );
    // Create an array to hold our data. Give the array
    // a default empty first row.
    var arrData = [[]];
    // Create an array to hold our individual pattern
    // matching groups.
    var arrMatches = null;
    // Keep looping over the regular expression matches
    // until we can no longer find a match.
    while (arrMatches = objPattern.exec( strData )){
        // Get the delimiter that was found.
        var strMatchedDelimiter = arrMatches[ 1 ];
        // Check to see if the given delimiter has a length
        // (is not the start of string) and if it matches
        // field delimiter. If id does not, then we know
        // that this delimiter is a row delimiter.
        if (strMatchedDelimiter.length &&
            strMatchedDelimiter !== strDelimiter){
            // Since we have reached a new row of data,
            // add an empty row to our data array.
            arrData.push( [] );
        }
        var strMatchedValue;
        // Now that we have our delimiter out of the way,
        // let's check to see which kind of value we
        // captured (quoted or unquoted).
        if (arrMatches[ 2 ]){
            // We found a quoted value. When we capture
            // this value, unescape any double quotes.
            strMatchedValue = arrMatches[ 2 ].replace(
                new RegExp( "\"\"", "g" ),
                "\""
                );
        } else {
            // We found a non-quoted value.
            strMatchedValue = arrMatches[ 3 ];
        }
        // Now that we have our value string, let's add
        // it to the data array.
        arrData[ arrData.length - 1 ].push( strMatchedValue );
    }
    // Return the parsed data.
    return( arrData );
}

//////////////////////////////////////
// FULLSCREEN CODE
//////////////////////////////////////
// I got most of this entire section from the Internet with little modification.
//  (ref: https://www.sitepoint.com/use-html5-full-screen-api/)

function goFullscreen() {
	// is full-screen enabled?
	if ( document.fullscreenEnabled || document.webkitFullscreenEnabled ||
			document.mozFullScreenEnabled || document.msFullscreenEnabled ) {
		// then go full-screen
		var html = document.documentElement;
		if (html.requestFullscreen) { html.requestFullscreen(); }
		else if (html.webkitRequestFullscreen) { html.webkitRequestFullscreen(); }
		else if (html.mozRequestFullScreen) { html.mozRequestFullScreen(); }
		else if (html.msRequestFullscreen) { html.msRequestFullscreen(); }
    }
}

function exitFullscreen() {
	// exit full-screen
	if (document.exitFullscreen) { document.exitFullscreen(); }
	else if (document.webkitExitFullscreen) { document.webkitExitFullscreen(); }
	else if (document.mozCancelFullScreen) { document.mozCancelFullScreen(); }
    else if (document.msExitFullscreen) { document.msExitFullscreen(); }
}

function toggleFullscreenButton() {
	// To be activated when entering or leaving fullscreen
	// changes the button text to match
	var fullscreenButton = document.getElementById("fullscreenButton");

	// are we full-screen?
	if ( document.fullscreenElement || document.webkitFullscreenElement ||
			document.mozFullScreenElement || document.msFullscreenElement ) {
		// If so, change the button to an exit-fullscreen button
		fullscreenButton.innerHTML = "Exit Fullscreen";
		fullscreenButton.onclick = exitFullscreen;
	}
	else {
		// Otherwise change the button to an enter-fullscreen button
	    fullscreenButton.innerHTML = "Go Fullscreen";
		fullscreenButton.onclick = goFullscreen;
    }
}

//////////////////////////////////////
// CHANGE IMAGE CODE
//////////////////////////////////////
// Declare static variables
var debugN = 0;

var frontImage;
var frontName;
var frontSrc;
var frontPath;
var frontColl;

var backImage;
var backName;
var backSrc;
var backPath;
var backColl;

var afterImage;

var nameLink;

var csvText;
var csvArray;

var interval;

function changeImage() {
	// Slow down the repetition of changing images to a reasonable speed.
//	if ( interval ) {
//		self.clearInterval(interval);
//		interval = null;
//		self.setInterval( changeImage, 9001 );
//	}

	debugN = debugN + 1;

	// Rotate images.
	var temp = afterImage;
	afterImage = frontImage;
	frontImage = backImage;
	backImage = temp;

	frontName = backName;
	frontSrc = backSrc;
	frontPath = backPath;
	frontColl = backColl;

	// Choose new work to push to back
	var ri = Math.floor( Math.random() * csvArray.length );
	// push it to back
	backName = csvArray[ ri ][ 0 ];
	backSrc = csvArray[ ri ][ 1 ];
	backPath = csvArray[ ri ][ 2 ];
	backColl = csvArray[ ri ][ 3 ];
	backImage.style.backgroundImage = "url(\"" + backSrc + "\")";

	// set proper placement
	frontImage.style.zIndex = 1;
	backImage.style.zIndex = -1;
	afterImage.style.zIndex = 0;

	// Fade in and out
	frontImage.style.opacity = 1; // CSS will fade in automatically
	afterImage.style.opacity = 0; // CSS will fade out automatically

	// Change text
	nameLink.href = "/collections/" + frontColl + "/" + frontPath;
	nameLink.innerHTML = frontName;
	console.log(frontSrc);
}

//////////////////////////////////////
// INITIALIZATION CODE
//////////////////////////////////////
// Initialize the frontImage and backImage variables
function initSlideshow() {
	// Initialize front and back images
	frontImage = document.getElementById( "slide1" );
	backImage = document.getElementById( "slide2" );
	afterImage = document.getElementById( "slide3" );

	frontImage.style.opacity = 0.0;
	backImage.style.opacity = 0.0;
	afterImage.style.opacity = 0.0;

	// Initialize the text box
	nameLink = document.getElementById("workLink");

    // retrieve array of all works currently in gallery
    csvArray = django_inputs;

    // prepare back image and front image
    var ri = Math.floor( Math.random() * csvArray.length );
    backName = csvArray[ ri ][ 0 ];
	backSrc = csvArray[ ri ][ 1 ];
	backPath = csvArray[ ri ][ 2 ];
	backColl = csvArray[ ri ][ 3 ];
	backImage.style.backgroundImage = "url(\"" + backSrc + "\")";

	var ri = Math.floor( Math.random() * csvArray.length );
    frontName = csvArray[ ri ][ 0 ];
    frontSrc = csvArray[ ri ][ 1 ];
    frontPath = csvArray[ ri ][ 2 ];
    frontColl = csvArray[ ri ][ 3 ];
    frontImage.style.backgroundImage = "url(\"" + frontSrc + "\")";

	// Set instance methods
    document.addEventListener( "fullscreenchange", toggleFullscreenButton );
    document.addEventListener( "webkitfullscreenchange", toggleFullscreenButton );
    document.addEventListener( "mozfullscreenchange", toggleFullscreenButton );
    document.addEventListener( "MSFullscreenChange", toggleFullscreenButton );

    setInterval(changeImage, 9001);
    changeImage();
}