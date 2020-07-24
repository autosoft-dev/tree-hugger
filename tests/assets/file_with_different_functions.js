/**
 * Representation of a rectangle
 */
class Rectangle {

  /**
   * Construct a rectangle
   */
  constructor(h, w) {
    this.h = h;
    this.w = w;
  }
  
  /**
   * Get the area of the rectangle
   */
  get area() {
    return this.computeArea();
  }

  computeArea() {
    return this.w * this.h;
  }
  
}

function utf8_to_b64(str) {
    try {
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function(match, p1) {
            return String.fromCharCode('0x' + p1);
         }));
    } catch(e) {
        console.log("conversion error", e);
    }
}
 
/**
 * @param {very_long_type} name           Description.
 * @param {type}           very_long_name Description.
 */
function test() {
	 alert("Hello Javatpoint");  
}

function multiply(a, b = 1) {
  return a * b;
}

function sum(...args) {
  return args.reduce((previous, current) => {
    return previous + current;
  });
}
