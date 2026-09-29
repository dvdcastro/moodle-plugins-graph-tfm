<?php
/**
 * User role assignment plugin version specification.
 *
 * @package    enrol
 * @subpackage dbuserrel
 * @copyright  Penny Leach <[email]>
 * @copyright  Maxime Pelletier <[email]>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2019071201;        // The current plugin version (Date: YYYYMMDDXX)
$plugin->requires  = 2012061700;        // Requires this Moodle version
$plugin->release   = '0.2';
$plugin->component = 'enrol_dbuserrel';  // Full name of the plugin (used for diagnostics)
$plugin->maturity  = MATURITY_BETA;
