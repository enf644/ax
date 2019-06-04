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
