// Resizes an image for a slideshow.
// See ../setHeight.js for a similar process
function resizeForSlideshow( imgToResize ) {
	// Get size of usable area for slideshow
	var usableWidth = window.innerWidth;
	var titleTable = document.getElementById( "descTable" );
	var windowHeight = window.innerHeight;
	var tableHeight = titleTable.offsetHeight;
	var usableHeight = windowHeight - tableHeight;

	// Resize containing div
	var slideDiv = document.getElementById( "slideDiv" );
	slideDiv.setAttribute( "style", "height:" + usableHeight + "px;" );

	// Get size of native image to be displayed
	var nativeWidth = imgToResize.naturalWidth;
	var nativeHeight = imgToResize.naturalHeight;

	// Determine width-to-height ratios of those two
	var windowRatio = usableWidth / usableHeight;
	var imageRatio = nativeWidth / nativeHeight;

	var parentNode = imgToResize.parentNode;

	if ( imageRatio > windowRatio ) {
		// image's width-to-height is greater than window
		// image should be set to 100% width, less height
		var newWidth = usableWidth;
		var newHeight = usableWidth * ( nativeHeight / nativeWidth );

		imgToResize.width = newWidth;
		imgToResize.height = newHeight;

		imgToResize.defWidth = newWidth;
		imgToResize.defHeight = newHeight;

		// resize and relocate image's container accordingly
		//parentNode.style.width = newWidth;
		//parentNode.style.height = newHeight;
		//parentNode.setAttribute( "style", "width:" + newWidth + "px;" );
		//parentNode.setAttribute( "style", "height:" + newHeight + "px;" );

		var newTop = ( usableHeight - imgToResize.height ) / 2;
		//parentNode.setAttribute( "style", "left:0;" );
		//parentNode.setAttribute( "style", "top:" + newTop + "px;" );
		imgToResize.style.left = 0;
		imgToResize.style.top = newTop + "px";

		imgToResize.defLeft = 0;
		imgToResize.defTop = newTop;
	}
	else {
		// image's width-to-height is less than window
		// image should be set to 100% height, less width
		var newWidth = usableHeight * ( nativeWidth / nativeHeight );
		var newHeight = usableHeight;

		imgToResize.height = newHeight;
		imgToResize.width = newWidth;

		imgToResize.defWidth = newWidth;
		imgToResize.defHeight = newHeight;

		// resize and relocate image's container accordingly
		//parentNode.setAttribute( "style", "width:" + newWidth + "px;" );
		//parentNode.setAttribute( "style", "height:" + newHeight + "px;" );

		// relocate image accordingly
		var newLeft = ( usableWidth - imgToResize.width ) / 2;
		/*parentNode.setAttribute( "style", "top:0;" );
		parentNode.setAttribute( "style", "left:" + newLeft + "px;" );*/
		imgToResize.style.top = 0;
		imgToResize.style.left = newLeft + "px";

		imgToResize.defLeft = newLeft;
		imgToResize.defTop = 0;

	}
}

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
	var fullscreenDiv = document.getElementById( "fullscreen" );

	// are we full-screen?
	if ( document.fullscreenElement || document.webkitFullscreenElement ||
			document.mozFullScreenElement || document.msFullscreenElement ) {
		// If so, change the button to an exit-fullscreen button
		fullscreenDiv.innerHTML = "\n\t\t<button id=\"exitFullscreenButton\" class=\"fsButton\" type=\"button\" onclick=\"exitFullscreen();\">Exit Fullscreen</button>\n\t";
	}
	else {
		// Otherwise change the button to an enter-fullscreen button
		fullscreenDiv.innerHTML = "\n\t\t<button id=\"fullscreenButton\" class=\"fsButton\" type=\"button\" onclick=\"goFullscreen();\">Go Fullscreen</button>\n\t";
	}
}


//////////////////////////////////////
// IMAGE TO FADE IN CODE
//////////////////////////////////////
var isActive = true;

var fadeInCt = 0;
var fadeInInterval;

// Increments the opacity of element by amt, until cap
function incrementOpacity( element, amt, cap ) {
	if ( !isActive ) {
	// only do stuff while user is looking
		return;
	}

	var currentOpacity = Number( window.getComputedStyle( element ).getPropertyValue( "opacity" ) );
	currentOpacity = currentOpacity + amt;
	element.style.opacity = currentOpacity;

	fadeInCt = fadeInCt + 1;

	if ( fadeInCt >= cap ) {
		element.style.opacity = 1;
		clearInterval( fadeInInterval );
	}
}

// Calls incrementOpacity to fill the specified interval.
function fadeIn( element, interval ) {
	var currentOpacity = Number( window.getComputedStyle( element ).getPropertyValue( "opacity" ) );
	fadeInCt = 0;
	if ( currentOpacity < 1 ) {
		cap = interval / 10.0;
		amt = 1.0 / cap;
		fadeInInterval = setInterval( incrementOpacity, 10, element, amt, cap );
	}
}

//////////////////////////////////////
// IMAGE TO FADE OUT CODE
//////////////////////////////////////
var fadeOutCt = 0;
var fadeOutInterval;

// Decrements the opacity of element by amt, until cap
function decrementOpacity( element, amt, cap ) {
	if ( !isActive ) {
	// only do stuff while user is looking
		return;
	}

	var currentOpacity = Number( window.getComputedStyle( element ).getPropertyValue( "opacity" ) );
	currentOpacity = currentOpacity - amt;
	element.style.opacity = currentOpacity;

	fadeOutCt = fadeOutCt + 1;

	if ( fadeOutCt >= cap ) {
		element.style.opacity = 0;
		clearInterval( fadeOutInterval );
	}
}

// Calls decrementOpacity to fill the specified interval.
function fadeOut( element, interval ) {
	var currentOpacity = Number( window.getComputedStyle( element ).getPropertyValue( "opacity" ) );
	fadeOutCt = 0;
	if ( currentOpacity > 0 ) {
		cap = interval / 10.0;
		amt = 1.0 / cap;
		fadeOutInterval = setInterval( decrementOpacity, 10, element, amt, cap );
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

var nameDiv;

var csvText;
var csvArray;

var interval;

function changeImage() {
	if ( !isActive ) {
	// only do stuff while user is looking
		return;
	}
	// Slow down the repetition of changing images to a reasonable speed.
	if ( interval ) {
		self.clearInterval(interval);
		interval = null;
		self.setInterval( changeImage, 9001 );
	}

	console.log( "Hello, World! #" + debugN );
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
	backImage.src = backSrc;

	// Resize appropriately, and redundantly
	resizeForSlideshow( frontImage );
	resizeForSlideshow( afterImage );
	resizeForSlideshow( backImage );

	// set proper placement
	frontImage.style.zIndex = 1;
	backImage.style.zIndex = -1;
	afterImage.style.zIndex = 0;

	// Fade in and out
	frontImage.style.opacity = 0; // going to fade in
	afterImage.style.opacity = 1; // going to fade out
	fadeIn( frontImage, 1000 );
	fadeOut( afterImage, 1000 );

	// Change text
	nameDiv.innerHTML = "\n\t\t\t\t\t\t<a href=\"collections/" + frontColl + "/" + frontPath +  "\">" + frontName + "</a>\n\t\t\t\t\t";
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
	nameDiv = document.getElementById( "workName" );

    // retrieve array of all works currently in gallery
    csvArray = django_inputs

    // prepare back image and front image
    var ri = Math.floor( Math.random() * csvArray.length );
    backName = csvArray[ ri ][ 0 ];
	backSrc = csvArray[ ri ][ 1 ];
	backPath = csvArray[ ri ][ 2 ];
	backColl = csvArray[ ri ][ 3 ];
	backImage.src = backSrc
	resizeForSlideshow( backImage )

	var ri = Math.floor( Math.random() * csvArray.length );
    frontName = csvArray[ ri ][ 0 ];
    frontSrc = csvArray[ ri ][ 1 ];
    frontPath = csvArray[ ri ][ 2 ];
    frontColl = csvArray[ ri ][ 3 ];
    frontImage.src = frontSrc;
    resizeForSlideshow( frontImage );

    interval = self.setInterval( changeImage, 1000 )

	// Set instance methods
	window.onfocus = function() { isActive = true; };
	window.onblur = function() { isActive = false; };
	document.addEventListener( "fullscreenchange", toggleFullscreenButton );
	document.addEventListener( "webkitfullscreenchange", toggleFullscreenButton );
	document.addEventListener( "mozfullscreenchange", toggleFullscreenButton );
	document.addEventListener( "MSFullscreenChange", toggleFullscreenButton );
}