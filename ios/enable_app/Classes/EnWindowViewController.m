//
//  EnWindowViewController.m
//  enable_app
//
//  Created by John Wiggins on 11/2/11.
//  Copyright (c) 2011 Enthought. All rights reserved.
//

#import "EnWindowViewController.h"

@implementation EnWindowViewController

@synthesize panRecognizer, pinchRecognizer, tapRecognizer, toolbar;

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (void)viewWillAppear:(BOOL)animated
{
    [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated
{
    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated
{
	[super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated
{
	[super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return YES;
}

# pragma mark - GestureRecognizer actions

- (IBAction)handlePanGesture:(UIGestureRecognizer *)gestureRecognizer
{
}

- (IBAction)handlePinchGesture:(UIGestureRecognizer *)gestureRecognizer
{
}

- (IBAction)handleTapGesture:(UIGestureRecognizer *)gestureRecognizer
{
    CGFloat const targetAlpha = MIN(1.0, ABS(self.toolbar.alpha - 1.0));
    BOOL const shouldHide = !self.toolbar.hidden;
    
    if (!shouldHide)
        self.toolbar.hidden = NO;

    [UIView animateWithDuration:0.2
                     animations:^{ self.toolbar.alpha = targetAlpha; }
                     completion:^(BOOL finished){ self.toolbar.hidden = shouldHide; }];
}

# pragma mark - GestureRecognizerDelegate methods

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer
       shouldReceiveTouch:(UITouch *)touch
{
    // Ignore gestures that start out by touching the toolbar.
    if (self.toolbar.hidden == NO)
    {
        CGPoint const posInToolbar = [touch locationInView:self.toolbar];
        if ([self.toolbar pointInside:posInToolbar withEvent:nil])
            return NO;
    }
    
    return YES;
}

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer
shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer
{
    return YES;
}

@end



