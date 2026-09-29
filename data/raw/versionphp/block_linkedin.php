<?php

/**
 * This plugin is to be used in combination with the LinkedIn authentication block
 *
 * @package    auth
 * @subpackage linkedin
 * @copyright  2013 Bas Brands, www.basbrands.nl
 * @author     Bas Brands [email]
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version  = 2013082100;
$plugin->requires = 2011120500;
$plugin->release = '1.1 (Build: 2012091800)';
$plugin->maturity = MATURITY_STABLE;
$plugin->component = 'block_linkedin';
$plugin->dependencies = array(
    'auth_linkedin'  => 2013082100,
);
