<?php
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
 * Version information for OpenAI ChatBot Block
 *
 * @package    block_openai_chatbot
 * @copyright  2025 Esteban Piazza <[email]>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'block_openai_chatbot';
$plugin->version = 2025100500; // YYYYMMDDHH format - Error Handling Improved
$plugin->requires = 2022112800; // Moodle 4.1 or later
$plugin->supported = [401, 404]; // Moodle 4.1 to 4.4
$plugin->maturity = MATURITY_STABLE;
$plugin->release = '1.0.0';
$plugin->dependencies = array();

// Additional plugin information
$plugin->cron = 0; // No cron needed for this block
$plugin->incompatible = null; // No incompatible versions