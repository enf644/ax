let axHost = null;

export function getAxHost() {
  if (axHost == null) {
    const scripts = document.getElementsByTagName('script');
    const index = scripts.length - 1;
    const myScript = scripts[index];
    const url = new URL(myScript.src);
    axHost = url.host;
  }
  return axHost;
}

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
// export function debounce(func, wait, immediate) {
//   let timeout;
//   console.log(wait);
//   return () => {
//     const context = this; const
//       args = arguments;
//     const later = () => {
//       timeout = null;
//       if (!immediate) func.apply(context, args);
//     };
//     const callNow = immediate && !timeout;
//     clearTimeout(timeout);
//     timeout = setTimeout(later, wait);
//     if (callNow) func.apply(context, args);
//   };
// }

export function debounce(callback, limit) {
  let wait = false;
  return function () {
    if (!wait) {
      callback.call();
      wait = true;
      setTimeout(() => {
        wait = false;
      }, limit);
    }
  };
}

export function getVersion() {
  return '0.0.1';
}
