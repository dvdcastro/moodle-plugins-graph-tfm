<?PHP
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Version information. When a new version is released the version is incremented
 *
 * @package    qtype_guessit
 * @subpackage guessit
 * @copyright  2025 Joseph Rézeau <[email]>
 * @copyright  based on GapFill by 2024 Marcus Green
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'qtype_guessit';
$plugin->dependencies = [
    'qbehaviour_guessit'   => 2025012600,
];
$plugin->version = 2025043000;
$plugin->requires = 2022111500;  // Moodle 4.1.
$plugin->release = '1.2';
$plugin->supported = [401, 405];
$plugin->maturity = MATURITY_STABLE;
