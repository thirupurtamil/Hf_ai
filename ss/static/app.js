var canvas = document.getElementById('canvas'),
    ctx = canvas.getContext('2d'),
    radius = canvas.height / 2;

// Translate the origin (0, 0) to the center of the circle
ctx.translate(radius, radius);

// Reduce the radius of the circle 
radius = radius * 0.90;

function drawClock() {
	drawFace(ctx, radius);
	drawTime(ctx, radius);

}

function drawFace(ctx, radius) {

	var angle,
		numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'], // Array for roman numbers
		i,
		j,
		k = 0;

	// Draw white circle
	ctx.beginPath();
	ctx.arc(0, 0, radius, 0, Math.PI * 2);
	ctx.fillStyle = '#ddd';
	ctx.lineWidth = radius * 0.01;
	ctx.stroke();
	ctx.fill();

	// Reset to default
	ctx.lineWidth = 1;
	ctx.fillStyle = '#000';

	// Draw center black circle
	ctx.beginPath();
	ctx.arc(0, 0, radius * 0.05, 0, Math.PI * 2);
	ctx.fill();

	// Draw outter yellow circle
	ctx.beginPath();
	ctx.strokeStyle = '#f9a825';
	ctx.lineWidth = radius * 0.02; 
	ctx.arc(0, 0, radius * 0.75, 0, Math.PI * 2);
	ctx.stroke();

	// Reset to default 
	ctx.lineWidth = 1;
	ctx.strokeStyle = '#000';
	ctx.fillStyle = '#000';

	// Draw inner circle
	ctx.beginPath();
	ctx.arc(0, 0, radius * 0.180, 0, Math.PI * 2);
	ctx.stroke();

	// Draw text
	ctx.textBaseline = 'middle';
	ctx.font = '20px Dancing Script';
	ctx.textAlign = 'center';
	ctx.fillText('tamilselvi', 0, -radius * 0.3);
	ctx.font = '15px Dancing Script';
	ctx.fillText('Pollachitamil', 0, radius * 0.4);

	

	// Draw lines
	for(i = 1; i < 61; i++) {
		// Divide circle into 60 equal parts --> Math.PI = 180 --> Math.PI / 130 (180 / 30) = 6
		angle = i * Math.PI / 30;

		// Every fifth line is thicker to represent hours on clock
		if(i === 5 || i === 10 || i === 15 || i === 20 || i === 25 || i === 30 || i === 35 || i === 40 || i === 45 || i === 50 || i === 55 || i === 60) 
			ctx.lineWidth = radius * 0.03;
		else
			ctx.lineWidth = 1;

		// Rotate coordinate system 
		ctx.rotate(angle);
		// Translate the origin (0, 0) to the edge of circle
		ctx.translate(0, radius);

		// Draw line
		ctx.beginPath();
		ctx.moveTo(0, 0);
		ctx.lineTo(0, -radius * 0.05);
		ctx.stroke();

		// Translate the origin (0, 0) back to the center of circle & rotate coordinate system back to default
		ctx.translate(0, -radius);
		ctx.rotate(-angle);
	}
	
	// Draw numbers
	for(j = 1; j < 13; j++) {
		// Divide circle into 12 equal parts for clock hours
		angle = j * Math.PI / 6;

		ctx.font = '30px sans';
		// Rotate coordinate system 
		ctx.rotate(angle);
		// Translate the origin (0, 0) to 0.85 of the radius
		ctx.translate(0, -radius * 0.85);
		while(k < numbers.length) {
			// Fill text with values from numbers array --> after first fill break from loop
			ctx.fillText(numbers[k], 0, 0);
			k++;
			break;
		}
		// Translate the origin (0, 0) back to centre of the circle & rotate coordinate system back to default
		ctx.translate(0, radius * 0.85);
		ctx.rotate(-angle);
	}
	
}

function drawTime(ctx, radius) {
	// Get current time (hour, minutes & seconds) from the Date object 
	var time = new Date(),
		hour = time.getHours(),
		minute = time.getMinutes(),
		second = time.getSeconds();

	// Calculate angle for hour on clock
	hour = hour % 12;
	hour = (hour * Math.PI / 6) + (minute * Math.PI / (6 * 60)) + (second * Math.PI / (360 * 60));
	// Draw hour hand
	drawHands(ctx, hour, radius * 0.04, radius * 0.5);

	// Calculate angle for minute on clock
	minute = (minute * Math.PI / 30) + (second * Math.PI / (30 * 60));
	// Draw minute hand
	drawHands(ctx, minute, radius * 0.02, radius * 0.75);

	// Calculate angle for second on clock
	second = (second * Math.PI / 30);
	// Draw second hand
	drawHands(ctx, second, radius * 0.01, radius * 0.9);

	// Reset to defaulta after three calls to drawHands function
	ctx.lineWidth = 1;
	ctx.lineCap = 'butt';

	// Draw center yellow circle
	ctx.beginPath();
	ctx.arc(0, 0, radius * 0.03, 0, Math.PI * 2);
	ctx.fillStyle = '#f9a825';
	ctx.fill();
}

function drawHands(ctx, position, width, length) {
		
	ctx.lineCap = 'round';
	ctx.lineWidth = width;
	// Draw hand
	ctx.beginPath();
	ctx.moveTo(0, 0);
	// Rotate hand depending on current time
	ctx.rotate(position);
	ctx.lineTo(0, -length);
	ctx.stroke();
	// Rotate back to default
	ctx.rotate(-position);
}


this.onload = function() {
	setInterval(function() {
		drawClock();
	}, 1000);
}










