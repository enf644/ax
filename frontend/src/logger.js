const logdown = require('logdown');

function backendLogTransport() { } // { msg, level, args, state }

logdown.transports = [backendLogTransport];
const logger = logdown('ax');
logger.state.isEnabled = true;

export default logger;
