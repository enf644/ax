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

export function getAxProtocol() {
  return 'http';
}


export function debounce(callback, limit) {
  let wait = false;
  return () => {
    if (!wait) {
      callback.call();
      wait = true;
      setTimeout(() => {
        wait = false;
      }, limit);
    }
  };
}

export function isGuid(strGuid) {
  const regexGuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return regexGuid.test(strGuid);
}

export function getVersion() {
  return '0.0.1';
}
