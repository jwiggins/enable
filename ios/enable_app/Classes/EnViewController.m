//
//  EnViewController.m
//  enable_app
//
//  Created by John Wiggins on 10/12/11.
//  Copyright Enthought 2011. All rights reserved.
//

#import "EnViewController.h"

@implementation EnViewController

@synthesize serverField;


/*
// The designated initializer. Override to perform setup that is required before the view is loaded.
- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        // Custom initialization
    }
    return self;
}
*/


// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
    serverField.delegate = self;
    
    [super viewDidLoad];
}



// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

- (void)didReceiveMemoryWarning
{
	// Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
	
	// Release any cached data, images, etc that aren't in use.
}

- (void)viewDidUnload
{
	self.serverField = nil;
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
    // Dismiss the keyboard
    [serverField resignFirstResponder];
    return YES;
}

- (void)textFieldDidEndEditing:(UITextField *)textField
{
    // Do something with the contents of serverField
}

- (void) dealloc
{
    serverField.delegate = nil;
}


@end
