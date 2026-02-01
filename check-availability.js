#!/usr/bin/env node

/**
 * Socceroof Availability Checker
 *
 * Usage: node check-availability.js <location> <date>
 * Example: node check-availability.js wall-street "2026-02-15"
 *
 * Locations: wall-street, crown-heights
 */

const { spawn } = require('child_process');
const { promisify } = require('util');
const exec = promisify(require('child_process').exec);

const LOCATIONS = {
  'wall-street': 'https://www.socceroof.com/en/book/club/wall-street/activity/rent-a-field/',
  'crown-heights': 'https://www.socceroof.com/en/book/club/crown-heights/activity/rent-a-field/'
};

async function runCommand(cmd) {
  try {
    const { stdout, stderr } = await exec(cmd);
    return { stdout, stderr, success: true };
  } catch (error) {
    return { stdout: error.stdout, stderr: error.stderr, success: false, error };
  }
}

async function checkAvailability(location, date) {
  const url = LOCATIONS[location];

  if (!url) {
    console.error(`Unknown location: ${location}`);
    console.error(`Available locations: ${Object.keys(LOCATIONS).join(', ')}`);
    process.exit(1);
  }

  console.log(`Checking availability for ${location} on ${date}...`);
  console.log(`URL: ${url}\n`);

  try {
    // Open the booking page
    await runCommand(`agent-browser open "${url}"`);
    await runCommand('agent-browser wait 3000');

    // Get snapshot to find interactive elements
    const snapshot = await runCommand('agent-browser snapshot -i --json');
    console.log('Page loaded. Looking for booking interface...\n');

    // Try to find and interact with the date picker
    // This will need to be customized based on the actual page structure
    await runCommand(`agent-browser find text "Activity Date" click`);
    await runCommand('agent-browser wait 1000');

    // Take a screenshot
    const screenshotPath = `/tmp/socceroof-${location}-${date}.png`;
    await runCommand(`agent-browser screenshot "${screenshotPath}"`);
    console.log(`Screenshot saved to: ${screenshotPath}`);

    // Get page content to parse availability
    const html = await runCommand('agent-browser get html body');

    // Close browser
    await runCommand('agent-browser close');

    return {
      location,
      date,
      screenshot: screenshotPath,
      // TODO: Parse availability from HTML
      available_times: []
    };

  } catch (error) {
    console.error('Error checking availability:', error);
    await runCommand('agent-browser close');
    process.exit(1);
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('Usage: node check-availability.js <location> <date>');
  console.log('Example: node check-availability.js wall-street "2026-02-15"');
  console.log(`\nAvailable locations: ${Object.keys(LOCATIONS).join(', ')}`);
  process.exit(1);
}

const [location, date] = args;
checkAvailability(location, date)
  .then(result => {
    console.log('\nResults:', JSON.stringify(result, null, 2));
  })
  .catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
