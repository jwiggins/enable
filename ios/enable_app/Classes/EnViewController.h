//
//  EnViewController.h
//  enable_app
//
//  Created by John Wiggins on 10/12/11.
//  Copyright Enthought 2011. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface EnViewController : UIViewController <UITextFieldDelegate>
{
    UITextField *serverField;
}

@property (nonatomic, retain) IBOutlet UITextField *serverField;

@end

